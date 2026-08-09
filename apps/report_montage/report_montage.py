from __future__ import annotations

import io
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageOps
import streamlit as st


BACKGROUND_RGB = (247, 245, 240)
CROP_CENTERS = ((0.5, 0.5), (0.25, 0.5), (0.75, 0.5), (0.5, 0.25), (0.5, 0.75))


@dataclass
class TileCandidate:
    source_index: int
    image: Image.Image
    mean_rgb: np.ndarray
    mean_lab: np.ndarray


@dataclass
class CandidateIndex:
    candidates: list[TileCandidate]
    lab_values: np.ndarray
    lab_squared_norms: np.ndarray
    source_indices: np.ndarray
    source_count: int


def load_image(uploaded_file, max_edge: int | None = None) -> Image.Image:
    """Load an upload consistently, including transparent and rotated images."""
    uploaded_file.seek(0)
    image = ImageOps.exif_transpose(Image.open(uploaded_file))
    if image.mode == "RGBA":
        background = Image.new("RGBA", image.size, BACKGROUND_RGB + (255,))
        image = Image.alpha_composite(background, image).convert("RGB")
    else:
        image = image.convert("RGB")
    if max_edge:
        image.thumbnail((max_edge, max_edge), Image.Resampling.LANCZOS)
    return image


def rgb_to_lab(rgb: np.ndarray) -> np.ndarray:
    """Convert sRGB values in the 0-255 range to CIE Lab for color matching."""
    values = rgb.astype(np.float32) / 255.0
    values = np.where(
        values <= 0.04045,
        values / 12.92,
        ((values + 0.055) / 1.055) ** 2.4,
    )

    x = (
        values[..., 0] * 0.4124 + values[..., 1] * 0.3576 + values[..., 2] * 0.1805
    ) / 0.95047
    y = values[..., 0] * 0.2126 + values[..., 1] * 0.7152 + values[..., 2] * 0.0722
    z = (
        values[..., 0] * 0.0193 + values[..., 1] * 0.1192 + values[..., 2] * 0.9505
    ) / 1.08883

    def transform(channel: np.ndarray) -> np.ndarray:
        return np.where(
            channel > 0.008856, np.cbrt(channel), 7.787 * channel + 16 / 116
        )

    fx, fy, fz = transform(x), transform(y), transform(z)
    return np.stack((116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)), axis=-1)


def make_cover_candidates(
    source_index: int, uploaded_file, tile_size: tuple[int, int]
) -> list[TileCandidate]:
    """Resize a cover once, then take its crop variants from that smaller image."""
    cover = load_image(uploaded_file)
    width, height = tile_size
    scale = max(width / cover.width, height / cover.height)
    resized_width = max(width, round(cover.width * scale))
    resized_height = max(height, round(cover.height * scale))
    resized = cover.resize((resized_width, resized_height), Image.Resampling.LANCZOS)
    max_left = resized_width - width
    max_top = resized_height - height
    candidates: list[TileCandidate] = []
    for center_x, center_y in CROP_CENTERS:
        left = round(max_left * center_x)
        top = round(max_top * center_y)
        tile = resized.crop((left, top, left + width, top + height))
        pixels = np.asarray(tile, dtype=np.float32)
        mean_rgb = pixels.mean(axis=(0, 1))
        candidates.append(
            TileCandidate(
                source_index=source_index,
                image=tile,
                mean_rgb=mean_rgb,
                mean_lab=rgb_to_lab(mean_rgb),
            )
        )
    cover.close()
    resized.close()
    return candidates


def make_candidate_index(cover_uploads, tile_size: tuple[int, int]) -> CandidateIndex:
    workers = min(8, len(cover_uploads))
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(make_cover_candidates, index, upload, tile_size)
            for index, upload in enumerate(cover_uploads)
        ]
        candidates = [candidate for future in futures for candidate in future.result()]
    lab_values = np.stack([candidate.mean_lab for candidate in candidates])
    return CandidateIndex(
        candidates=candidates,
        lab_values=lab_values,
        lab_squared_norms=(lab_values**2).sum(axis=1),
        source_indices=np.array(
            [candidate.source_index for candidate in candidates], dtype=np.int32
        ),
        source_count=len(cover_uploads),
    )


def montage_dimensions(
    reference: Image.Image, columns: int, long_edge: int
) -> tuple[int, int, int, tuple[int, int]]:
    reference_ratio = reference.height / reference.width
    if reference.width >= reference.height:
        output_width = long_edge
        output_height = max(1, round(long_edge * reference_ratio))
    else:
        output_height = long_edge
        output_width = max(1, round(long_edge / reference_ratio))
    rows = max(1, round(columns * output_height / output_width))
    return (
        output_width,
        output_height,
        rows,
        (max(8, round(output_width / columns)), max(8, round(output_height / rows))),
    )


def adapt_tile(
    tile: Image.Image, source_mean: np.ndarray, target_mean: np.ndarray, strength: float
) -> Image.Image:
    if strength == 0:
        return tile
    scale = np.clip(target_mean / np.maximum(source_mean, 1), 0.35, 2.8)
    pixels = np.asarray(tile, dtype=np.float32)
    pixels *= 1 + strength * (scale - 1)
    return Image.fromarray(np.clip(pixels, 0, 255).astype(np.uint8), mode="RGB")


def build_montage(
    reference: Image.Image,
    candidate_index: CandidateIndex,
    columns: int,
    long_edge: int,
    max_reuse: int,
    adaptation: float,
) -> tuple[Image.Image, int, int]:
    output_width, output_height, rows, _ = montage_dimensions(
        reference, columns, long_edge
    )
    reference_pixels = np.asarray(
        reference.resize((output_width, output_height), Image.Resampling.LANCZOS),
        dtype=np.float32,
    )
    usage = np.zeros(candidate_index.source_count, dtype=np.int32)
    montage = Image.new("RGB", (output_width, output_height), BACKGROUND_RGB)

    for row in range(rows):
        top = round(row * output_height / rows)
        bottom = round((row + 1) * output_height / rows)
        for column in range(columns):
            left = round(column * output_width / columns)
            right = round((column + 1) * output_width / columns)
            cell = reference_pixels[top:bottom, left:right]
            target_rgb = cell.mean(axis=(0, 1))
            target_lab = rgb_to_lab(target_rgb)
            distances = (
                candidate_index.lab_squared_norms
                - 2 * candidate_index.lab_values @ target_lab
                + (target_lab**2).sum()
            )

            if max_reuse:
                eligible = usage[candidate_index.source_indices] < max_reuse
                if eligible.any():
                    distances = np.where(eligible, distances, np.inf)

            chosen = candidate_index.candidates[int(np.argmin(distances))]
            usage[chosen.source_index] += 1
            tile = adapt_tile(chosen.image, chosen.mean_rgb, target_rgb, adaptation)
            montage.paste(
                tile.resize((right - left, bottom - top), Image.Resampling.LANCZOS),
                (left, top),
            )

    return montage, rows, columns


def encode_png(image: Image.Image) -> bytes:
    output = io.BytesIO()
    image.save(output, format="PNG", optimize=True)
    return output.getvalue()


def candidate_cache_key(cover_uploads, tile_size: tuple[int, int]) -> tuple:
    return (
        tile_size,
        tuple(
            (
                getattr(upload, "file_id", None),
                upload.name,
                upload.size,
            )
            for upload in cover_uploads
        ),
    )


st.title("Annual Report Montage")
st.caption("Rebuild a reference image from your annual-report covers.")

with st.sidebar:
    st.subheader("Mosaic settings")
    columns = st.slider(
        "Tile density",
        min_value=12,
        max_value=72,
        value=36,
        help="More columns create a finer mosaic and take longer to render.",
    )
    long_edge = st.select_slider(
        "PNG long edge", options=[900, 1200, 1800, 2400, 3000, 3600], value=1800
    )
    max_reuse = st.number_input(
        "Max repeats per cover",
        min_value=0,
        max_value=1_000,
        value=0,
        help="Set to 0 to allow a cover to be reused without a limit.",
    )
    adaptation = st.slider(
        "Color adaptation",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.05,
        help="Higher values more closely match the reference colors.",
    )

st.write(
    "Upload one image to recreate, then add the report covers that will become its tiles."
)
input_column, source_column = st.columns(2)
with input_column:
    reference_upload = st.file_uploader(
        "Reference image", type=["png", "jpg", "jpeg", "webp"], key="montage_reference"
    )
with source_column:
    cover_uploads = st.file_uploader(
        "Annual-report covers",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True,
        key="montage_covers",
    )

if cover_uploads:
    st.caption(
        f'{len(cover_uploads)} cover image{"s" if len(cover_uploads) != 1 else ""} ready for matching.'
    )

generate = st.button(
    "Generate montage",
    type="primary",
    disabled=reference_upload is None or not cover_uploads,
)
if generate:
    try:
        started_at = time.perf_counter()
        reference = load_image(reference_upload, max_edge=long_edge)
        _, _, _, tile_size = montage_dimensions(reference, columns, long_edge)
        cache_key = candidate_cache_key(cover_uploads, tile_size)
        index_reused = cache_key == st.session_state.get("report_montage_index_key")
        if index_reused:
            candidate_index = st.session_state["report_montage_index"]
        else:
            with st.spinner("Indexing cover colors and crop variations..."):
                candidate_index = make_candidate_index(cover_uploads, tile_size)
            st.session_state["report_montage_index_key"] = cache_key
            st.session_state["report_montage_index"] = candidate_index

        with st.spinner("Matching cover crops to the reference..."):
            montage, rows, rendered_columns = build_montage(
                reference,
                candidate_index,
                columns=columns,
                long_edge=long_edge,
                max_reuse=int(max_reuse),
                adaptation=adaptation,
            )
        st.session_state["report_montage_png"] = encode_png(montage)
        st.session_state["report_montage_meta"] = {
            "duration": time.perf_counter() - started_at,
            "rows": rows,
            "columns": rendered_columns,
            "size": montage.size,
            "index_reused": index_reused,
        }
    except Exception as error:
        st.error(f"Unable to create the montage: {error}")

if "report_montage_png" in st.session_state:
    metadata = st.session_state["report_montage_meta"]
    st.divider()
    preview_column, details_column = st.columns([3, 1])
    with preview_column:
        st.image(
            st.session_state["report_montage_png"],
            caption="Generated montage",
            width='stretch',
        )
    with details_column:
        st.subheader("Output")
        st.write(f"{metadata['size'][0]} x {metadata['size'][1]} px")
        st.write(f"{metadata['columns']} x {metadata['rows']} tiles")
        st.caption(f"Rendered in {metadata['duration']:.1f} seconds.")
        if metadata["index_reused"]:
            st.caption("Reused the existing cover index.")
        st.download_button(
            "Download PNG",
            data=st.session_state["report_montage_png"],
            file_name="annual-report-montage.png",
            mime="image/png",
            type="primary",
        )
