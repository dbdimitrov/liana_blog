+++
title = "LIANA+ moves to scverse"
date = 2026-11-09T00:00:00+01:00
description = "LIANA+ 2.0 lives in the scverse organization and follows scverse conventions."
author = "Muskan Hashim, Daniel Dimitrov"
draft = false
+++

[LIANA+](https://github.com/scverse/liana) has moved from `saezlab/liana-py` into the scverse GitHub organization where it now lives as `scverse/liana` and continues to be maintained by Daniel Dimitrov.
Alongside the move, version 2.0 brings LIANA+ in line with the conventions the rest of the ecosystem follows.

<img src="/img/blog/liana_x_scverse_overview.svg" style="max-width: 100%;" alt="LIANA+ x scverse Overview." />

## LIANA+ infers cell-cell communication from single-cell and spatial data

[LIANA+](https://doi.org/10.1038/s41556-024-01469-w) is a framework for studying cell-cell communication in single-cell and spatially resolved omics data (including multimodal data).
It works directly on [AnnData](https://anndata.scverse.org/) and [MuData](https://github.com/scverse/mudata) objects just like [scanpy](https://scanpy.scverse.org/) and [squidpy](https://squidpy.readthedocs.io/en/stable/) do.
At its core, LIANA+ re-implements a range of established ligand-receptor methods and lets you combine their results into a consensus ranking with `li.mt.rank_aggregate`.
For prior knowledge it draws on [OmniPath](https://omnipathdb.org/) with [MetalinksDB](https://github.com/biocypher/metalinks) adding metabolite-receptor interactions.
For comparisons across samples and conditions LIANA+ connects to [MOFA+](https://biofam.github.io/MOFA2/) and [Tensor-cell2cell](https://earmingol.github.io/cell2cell/) to find communication patterns without a predefined contrast.
When there is a specific contrast in mind, it works with [pyCrossTalkeR](https://github.com/CostaLab/pyCrossTalkeR) for network-based differential analysis and with [corneto](https://github.com/saezlab/corneto) to infer downstream signalling networks.
If you are not sure where to start, the [decision tree](https://github.com/scverse/liana#decision-tree) in the README leads from your type of data to a suitable method and its tutorial.

Over the past year LIANA+ has also gained an Agent Skill for [Claude Code](https://claude.com/claude-code) along with two spatial methods for data at single-cell resolution.
## An Agent Skill helps Claude Code choose the right method

LIANA+ now ships with an [Agent Skill](https://docs.claude.com/en/docs/claude-code/skills) for Claude Code encoding the decision tree so that the agent picks a method that suits your data with the right defaults and knows where the results land.
This would only be needed to be installed once, after installing liana:

```shell
liana-install-skills
```

This copies the skill to `~/.claude/skills/liana/`, where Claude Code picks it up in every project.
After upgrading liana you can refresh it with `liana-install-skills --force`.
From there you can describe liana tasks in plain words, such as "compare interactions between conditions".

## LRIC and the Inflow score target single-cell resolution spatial data

LRIC and the Inflow score are both designed for spatial technologies that resolve individual cells, such as MERFISH.

- **LRIC** (`li.mt.lric`) extends the cross pair-correlation function by weighting sender cells by their ligand expression and receiver cells by their receptor expression to show at which distances a ligand-receptor pair is enriched or depleted (see the [LRIC tutorial](https://liana.readthedocs.io/en/stable/tutorials/notebooks/LRIC_tutorial.html)).
- **The Inflow score** (`li.mt.inflow`) measures how strongly each cell receives ligand signals from its spatial neighborhood while accounting for spatial proximity and the cell type sending the signal (see the [Inflow tutorial](https://liana.readthedocs.io/en/stable/tutorials/notebooks/inflow_score.html)).

As an example, here is the cell-type-informed mode of LRIC from the tutorial on a MERFISH section of the adult mouse brain with interactions ranked by how enriched they are at short range:

```py
import liana as li

resource = li.rs.select_resource("mouseconsensus")

li.mt.lric(
    adata,
    resource=resource,
    groupby="cell_type",
    spatial_key="X_spatial_coords",
    max_radius=250,
    radius_step=20,
    expr_prop=0.2,
    use_raw=False,
    key_added="lric_ct",
)

# short-range interactions (max_dist=50 µm) by area under log2 g(r) curve
lric_ct_res = li.mt.get_lric_auc(adata, "lric_ct", max_dist=50, min_bins=2)
print(lric_ct_res.head(3).to_string(index=False))
```

```text
                        source                         target ligand_complex receptor_complex  interaction    score  peak_radius
  vascular leptomeningeal cell choroid plexus epithelial cell        Col18a1             Gpc4 Col18a1^Gpc4 3.896359         40.0
choroid plexus epithelial cell                 ependymal cell        Sostdc1             Lrp4 Sostdc1^Lrp4 3.759549         40.0
choroid plexus epithelial cell                 ependymal cell        Col18a1             Gpc4 Col18a1^Gpc4 3.735166         40.0
```

A score above 0 means the ligand-receptor pair is co-enriched at short range and a score of 1 roughly corresponds to a two-fold enrichment.
Both methods were added fairly recently so their API may still change slightly.

## Version 2.0 follows scverse conventions

The namespaces now mirror the scanpy layout (`li.pp`, `li.mt`, `li.pl`, `li.ms`, `li.ds` and `li.rs`).
`use_raw` now defaults to `False` as it does in squidpy and [decoupler](https://decoupler.readthedocs.io/en/latest/) so methods read from `adata.X` unless you tell them otherwise.
Under the hood, the codebase is synced with the [scverse package template](https://github.com/scverse/cookiecutter-scverse) and type-checked with [mypy](https://github.com/python/mypy) in CI.
The release also includes an audit of the codebase with several fixes that affect results so numbers may shift when you upgrade (this is intended).

## Existing code needs new import paths and defaults

If you already use LIANA+, most of what changes for you comes down to import paths and a few defaults:

| 1.x | 2.0 |
|---|---|
| `li.ut.spatial_neighbors` and other preprocessing helpers | `li.pp` |
| `li.ut.get_factor_scores` and related helpers | `li.ms` |
| `li.mu` | renamed to `li.ms` (multisample) |
| `li.testing` | renamed to `li.ds` (datasets) |
| `use_raw=True` by default | `use_raw=False`; pass `use_raw=True` to keep reading `.raw` |
| spatial weighting whenever `obsm["spatial"]` exists | opt-in via `spatial_key` |
| `expr_prop=0.1` in single-cell methods and `rank_aggregate` | `expr_prop=0.05` |

Version 2.1 also removes the `pair_chunk` and `transform_fn` arguments from `li.mt.lric` and you can find every other change in the [changelog](https://github.com/scverse/liana/blob/main/CHANGELOG.md).

## Get started

LIANA+ is available on PyPI:

```shell
pip install liana
```

The [documentation](https://liana.readthedocs.io/en/latest/) has tutorials for each method and issues or contributions are welcome on [GitHub](https://github.com/scverse/liana).
If you are new to scverse, [scverse.org/join](/join/) is a good place to start.

<br>

*the scverse team.*
