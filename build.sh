#!/usr/bin/env bash
set -e

echo "📦 Cleaning early builds..."
rm -rf build dist Colorizer.spec

echo "🚀 Building with PyInstaller..."

pyinstaller \
    main.py \
    --name="Glow Engine Colorizer Utility" \
    --icon="icon.png" \
    --add-data="icon.png:." \
    --add-data="core:core" \
    --add-data="utils:utils" \
    --add-data="widgets:widgets" \
    --windowed \
    --noconfirm \
    --collect-all sklearn \
    --collect-all numpy \
    --collect-all pillow \
    --hidden-import="PIL.Image" \
    --hidden-import="PIL.ImageDraw" \
    --hidden-import="PIL.ImageFilter" \
    --hidden-import="PIL.ImageOps" \
    --hidden-import="PIL.ImageEnhance" \
    --hidden-import="PIL.ImageChops" \
    --hidden-import="PIL.ImageSequence" \
    --hidden-import="PIL.GifImagePlugin" \
    --hidden-import="PIL.BmpImagePlugin" \
    --hidden-import="PIL.JpegImagePlugin" \
    --hidden-import="PIL.PngImagePlugin" \
    --hidden-import="PIL.TiffImagePlugin" \
    --hidden-import="sklearn.cluster._kmeans_lloyd" \
    --hidden-import="sklearn.cluster._kmeans_elkan" \
    --hidden-import="sklearn.metrics._pairwise_distances_reduction._middle_term_computer" \
    --hidden-import="sklearn.metrics._pairwise_distances_reduction._datasets_pair" \
    --hidden-import="sklearn.metrics._pairwise_distances_reduction._base" \
    --hidden-import="sklearn.utils._openmp_helpers" \
    --hidden-import="sklearn.utils._random" \
    --hidden-import="sklearn.utils._heap" \
    --hidden-import="sklearn.utils._seq_dataset" \
    --hidden-import="sklearn.utils._weight_vector"

echo "✅ Build finished!"
echo ""
echo "🔧 to debug, run::"
echo "bash debug_app.sh"
