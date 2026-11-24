"""Usage: python make_figs.py <out_dir> [path/to/yao_2023.h5ad]

Ntf3^Ntrk3 (glutamatergic neuron -> neuroblast) in the hippocampus: LRIC restricted to the hippocampus, inflow on the whole slide with the hippocampus outlined;
same resource, matched spatial scale (inflow gaussian bw=27 um, cutoff 0.1 -> ~58 um; LRIC up to 120 um)."""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import plotnine as p9
import scanpy as sc
import liana as li

OUT = sys.argv[1]
DATA = sys.argv[2] if len(sys.argv) > 2 else None
sk = "X_spatial_coords"
NAVY = "#383f56"
SRC, TGT, INT = "glutamatergic neuron", "neuroblast (sensu Vertebrata)", "Ntf3^Ntrk3"

if DATA:
    import anndata as ad
    a = ad.read_h5ad(DATA)
else:
    a = li.ds.yao_2023()  # ~1GB download on first call
a = a[a.obs["brain_section_label"] == "C57BL6J-2.039"].copy()
a.var_names = a.var["gene_name"].astype(str)
a.var_names_make_unique()
sc.pp.filter_cells(a, min_genes=10)
sc.pp.filter_genes(a, min_cells=3)
sc.pp.normalize_total(a, target_sum=1e4)
sc.pp.log1p(a)
full = a.copy()  # whole slide, used for inflow
a = a[a.obs["major_brain_region"] == "Hippocampus"].copy()
# keep the main hippocampal piece: drop small detached fragments annotated as hippocampus
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree
import numpy as np
xy = a.obsm[sk]
n_comp, comp = connected_components(cKDTree(xy).sparse_distance_matrix(cKDTree(xy), 100, output_type="coo_matrix"), directed=False)
a = a[comp == np.bincount(comp).argmax()].copy()
print("kept", a.n_obs, "cells in the main hippocampal component of", n_comp)
vc = a.obs["cell_type"].value_counts()
a = a[a.obs["cell_type"].isin(vc[vc >= 50].index)].copy()
a.obs["cell_type"] = a.obs["cell_type"].astype(str).astype("category")
res = li.rs.select_resource("mouseconsensus")

# LRIC (cell-type informed)
li.mt.lric(a, resource=res, groupby="cell_type", spatial_key=sk, max_radius=120, radius_step=20,
           expr_prop=0.1, use_raw=False, key_added="lric_ct")
p = li.pl.lric_lineplot(a, "lric_ct", source=SRC, target=TGT, interaction=INT,
                        figure_size=(8, 4.2), return_fig=True)
p = (p
     + p9.scale_color_manual(
         breaks=["g (full)", "g_pcf", "g_expr"],
         values={"g (full)": "#e0216b", "g_pcf": "#f07800", "g_expr": "#12a89d"},
         labels=["Full LRIC", "Cell-type co-localisation", "Ligand-receptor expression"])
     + p9.labs(title="Ntf3 -> Ntrk3: glutamatergic neurons -> neuroblasts (hippocampus)",
               x="Distance (µm)", y="g(r)  (1 = random)")
     + p9.theme_minimal()
     + p9.theme(figure_size=(8, 4.2),
                plot_title=p9.element_text(size=11, color=NAVY, weight="bold"),
                axis_title=p9.element_text(color=NAVY), axis_text=p9.element_text(color=NAVY),
                legend_text=p9.element_text(color=NAVY),
                panel_grid_minor=p9.element_blank(),
                panel_grid_major=p9.element_line(color="#e3e7f0"),
                plot_background=p9.element_rect(fill="white", color="white")))
p.save(f"{OUT}/lric_ntf3_ntrk3.png", dpi=200, verbose=False)

# Inflow on the whole slide (same resource and bandwidth), hippocampus outlined
hippo_xy = a.obsm[sk]
li.pp.spatial_neighbors(adata=full, bandwidth=27, spatial_key=sk)
lr = li.mt.inflow(full, groupby="cell_type", resource=res, nz_prop=0.01, use_raw=False)
var = f"{SRC}^{INT}"
fig, ax = plt.subplots(figsize=(6.5, 6))
sc.pl.embedding(lr, basis=sk, color=var, s=5, cmap="magma", frameon=False, ax=ax, show=False,
                title="Ntf3 -> Ntrk3 inflow from glutamatergic neurons")
# outline: rasterise hippocampus cells, close gaps, fill, contour
from scipy import ndimage
step = 15.0
x0, y0 = full.obsm[sk].min(0) - 5 * step
x1, y1 = full.obsm[sk].max(0) + 5 * step
H, xe, ye = np.histogram2d(hippo_xy[:, 0], hippo_xy[:, 1], bins=[np.arange(x0, x1, step), np.arange(y0, y1, step)])
m = ndimage.binary_fill_holes(ndimage.binary_closing(H > 0, structure=np.ones((5, 5)), iterations=2))
m = ndimage.binary_opening(m, structure=np.ones((3, 3)))
m = ndimage.gaussian_filter(m.astype(float), sigma=1.5)  # smooth the staircase edge
xc, yc = (xe[:-1] + xe[1:]) / 2, (ye[:-1] + ye[1:]) / 2
import matplotlib.patheffects as pe
OUTLINE = "#12a89d"
halo = [pe.withStroke(linewidth=5.5, foreground="white")]
cs = ax.contour(xc, yc, m.T, levels=[0.5], colors=[OUTLINE], linewidths=2.6, linestyles="--")
for c in getattr(cs, "collections", [cs]):
    c.set_path_effects(halo)
# label just above the outline's top edge
top = hippo_xy[hippo_xy[:, 1].argmax()] if ax.yaxis_inverted() is False else hippo_xy[hippo_xy[:, 1].argmin()]
ax.annotate("Hippocampus", xy=(hippo_xy[:, 0].mean(), top[1]), xytext=(0, 14 if not ax.yaxis_inverted() else -14),
            textcoords="offset points", ha="center", va="center", fontsize=13, fontweight="bold", color=OUTLINE,
            path_effects=halo)
fig.savefig(f"{OUT}/inflow_ntf3_ntrk3.png", dpi=200, bbox_inches="tight", facecolor="white")
print(lr.obs.groupby("cell_type", observed=True).apply(
    lambda d: lr[d.index, var].X.mean()).sort_values(ascending=False).head(6))
print("done")
