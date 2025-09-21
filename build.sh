#!/usr/bin/env bash
set -e

echo "📦 Limpando builds anteriores..."
rm -rf build dist Colorizer.spec

echo "🚀 Construindo com PyInstaller..."

pyinstaller \
    colorizer.py \
    --name="Glow Engine Colorizer Utility" \
    --icon="icon.png" \
    --add-data="icon.png:." \
    --windowed \
    --noconfirm \
    --collect-all sklearn \
    --collect-all numpy \
    --collect-all pillow \
    --hidden-import="sklearn.cluster._kmeans_lloyd" \
    --hidden-import="sklearn.cluster._kmeans_elkan" \
    --hidden-import="sklearn.metrics._pairwise_distances_reduction._middle_term_computer" \
    --hidden-import="sklearn.metrics._pairwise_distances_reduction._datasets_pair" \
    --hidden-import="sklearn.metrics._pairwise_distances_reduction._base" \
    --hidden-import="sklearn.utils._openmp_helpers" \
    --hidden-import="sklearn.utils._random" \
    --hidden-import="sklearn.utils._heap" \
    --hidden-import="sklearn.utils._seq_dataset" \
    --hidden-import="sklearn.utils._weight_vector" \
    --hidden-import="PIL._imaging" \
    --hidden-import="PIL.JpegImagePlugin" \
    --hidden-import="PIL.PngImagePlugin" \
    --hidden-import="PIL.TiffImagePlugin"

echo "✅ Build concluído!"
echo ""
echo "🔧 Para rodar no terminal (para capturar logs):"
echo "./dist/Colorizer/Colorizer.app/Contents/MacOS/Glow Engine Colorizer Utility"
