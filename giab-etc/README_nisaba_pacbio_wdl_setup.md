# Running PacBio WDL Pipelines on NISABA

Documentation for the NIST-GIAB Team.

PacBio has whole genome HiFi analysis pipelines for;

- [Germline](https://github.com/PacificBiosciences/HiFi-human-WGS-WDL)
- [Somatic](https://github.com/PacificBiosciences/wdl-hifisomatic) (early access not publicly released yet)

Following setup used by ND Olson to run the germline pipeline. 


GRCh38 implemented by PacBio, modified to work with GRCh37 and CHM13[^1].
Germline pipeline was modified to run with multiple references, [GIAB-Germline](https://github.com/nate-d-olson/HiFi-human-WGS-WDL-GIAB).

## Steps

1. Clone GIAB modified version of the pipeline [GIAB-Germline](https://github.com/nate-d-olson/HiFi-human-WGS-WDL-GIAB)
1. [Getting input files(#getting-pipeline-input-files)
1. [Setting up environment](#setting-up-environment)
1. [Completing input config file](#completing-input-config)
1. [Running pipeline](#running-pipeline)

## Cloning Repo

Using ssh connection

```sh
git clone git@github.com:nate-d-olson/HiFi-human-WGS-WDL-GIAB.git
```

Using http
```sh
git clone https://github.com/nate-d-olson/HiFi-human-WGS-WDL-GIAB.git
```

## Getting pipeline input files

- [Get reference genome files](#getting-Reference-files)
- Input ubams, download/ copy to directory accessible on nisaba

## Setting up environment

Micromamba used to install pipeline dependencies required for running pipeline, specifically `miniwdl` for executing pipeline and `singularity` for task dependencies.

### Creating Mamba Environment

Creating `miniwdl` mamba environment with `miniwdl-slurm` and `singularity`

- `"${SHELL}" <(curl -L micro.mamba.pm/install.sh)`, answered y/ confirmed all choices. This should modify `~/.bashrc` to add `micromamba` to your path.
- Activating micromamba base environment `micromamba activate` (this step might not be necessary to create `miniwdl` env)
- Creating environment for running pipelines `micromamba create --name miniwdl {giab-etc/env.yml}`
- Activating miniwdl mamba env `micromamba activate miniwdl`
- Check that miniwdl (`miniwdl --version`) and singularity (`singularity --version`) available.

### Configuring to run on nisaba

`miniwdl` configuration file for using miniwdl as the execution engine to run WDL pipelines on nisaba[^4]. 

- Copy `giab-etc/miniwdl.cgf` to `~/.config/miniwdl.cfg`.   
- Modify `[singularity]` section appropriate path for singularity, e.g. `exe = ["/home/nolson/micromamba/bin/singularity"]`[^5]
- Added `export TMPDIR=/scratch/` to the end of `~/.bashrc` to use nisaba admin preferred scratch directory

## Completing input config

Modify the template [inputs.json](https://github.com/PacificBiosciences/HiFi-human-WGS-WDL/blob/main/backends/hpc/inputs.hpc.json) config file with sample information and input file paths.[^6]

Example json files in `giab-etc` for AJTrio and HG008 runs by ND Olson, also see [example pipeline run](#example-pipeline-run).

## Running Pipeline

Run the pipeline using tmux so you can detach and re-attach to the session.

`tmux new-session -t {hifi}` (or whatever session name you want to use)

In the tmux session activate mamba environment using `micromamba activate miniwdl`

Start pipeline run note paths should be relative to where you want to run the pipeline

```sh
miniwdl run {relative path to repo}/HiFi-human-WGS-WDL/workflows/main.wdl \
    -i {inputs.json} \
    -d {output directory}
```

The tmux session will provide real-time run status with elapsed time, number of tasks completed, ready, and running, along with resources allocated for the running jobs.

See `{output directory}/_LAST/workflow.log` for high level log of latest run.
Subdirectories have task and subworkflow log files.
The task and workflow log files have entries from the high level log file specific to the task or subworkflow.
The individual task subdirectories have `stderr.txt`, `stdout.txt`, and `slurm_singularity.log.txt` with command and slurm log files.


## Supplemental

### Getting Reference Files

__The read aligner `pbmm2`(a minimap2 wrapper for pacbio HiFi) requires reference genome files be unzipped.__

Reference files in `dataset/{GRCh37,GRCh38,CHM13}`

create directories for references

```sh
mkdir -p dataset/{GRCh37,GRCh38,CHM13}
```

PacBio has a [github repository](https://github.com/PacificBiosciences/reference_genomes) with shell script for downloading and retirieving reference data files.

#### GRCh37

Downloading reference fasta from ftp, decompressing, and indexing.

```sh
wget https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/release/references/GRCh37/hs37d5.fa.gz
mv hs37d5.fa.gz dataset/GRCh37/
cd dataset/GRCh37
gunzip hs37d5.fa.gz
samtools faidx hs37d5.fa
```



Creating chromosome lengths files

```sh
cut -f1,2 hs37d5.fa.fai > hs37d5.chr_lengths.txt
```


Downloaded tandem repeat file

```sh
wget https://github.com/PacificBiosciences/pbsv/blob/master/annotations/human_hs37d5.trf.bed
```

Download files for HiFiCNV (not currently used with modified pipeline)

```sh
wget https://github.com/PacificBiosciences/HiFiCNV/blob/7b0622788cbfbf571c34fff55924991b6c688893/data/excluded_regions/cnv.excluded_regions.hs37d5.bed.gz
wget https://github.com/PacificBiosciences/HiFiCNV/blob/7b0622788cbfbf571c34fff55924991b6c688893/data/excluded_regions/cnv.excluded_regions.hs37d5.bed.gz.tbi
wget https://github.com/PacificBiosciences/HiFiCNV/blob/7b0622788cbfbf571c34fff55924991b6c688893/data/expected_cn/expected_cn.hs37d5.XX.bed
wget https://github.com/PacificBiosciences/HiFiCNV/blob/7b0622788cbfbf571c34fff55924991b6c688893/data/expected_cn/expected_cn.hs37d5.XY.bed
```

Chrom splits file generated using python script by ND Olson `make_chrom_splits_json.py`

#### GRCh38-GIABv3

Download reference genome and index.

```sh
wget -qO - ftp://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/001/405/GCA_000001405.15_GRCh38/seqs_for_alignment_pipelines.ucsc_ids/GCA_000001405.15_GRCh38_no_alt_analysis_set.fna.gz \
    | gunzip -c > human_GRCh38_no_alt_analysis_set.fasta
samtools faidx human_GRCh38_no_alt_analysis_set.fasta
cut -f1,2 human_GRCh38_no_alt_analysis_set.fasta.fai > human_GRCh38_no_alt_analysis_set.chr_lengths.txt
```

Download and reformat Ensembl GFF[^2].

```sh
wget -qO - ftp://ftp.ensembl.org//pub/release-101/gff3/homo_sapiens/Homo_sapiens.GRCh38.101.gff3.gz | gunzip -c \
    | awk -v OFS="\t" '{if ($1=="##sequence-region") && ($2~/^G|K/) {print $0;} else if ($0!~/G|K/) {print "chr" $0;}}' \
    | bgzip > ensembl.GRCh38.101.reformatted.gff3.gz
```

Download tandem repeat annotations for pbsv

```sh
wget https://github.com/PacificBiosciences/pbsv/raw/master/annotations/human_GRCh38_no_alt_analysis_set.trf.bed
```

PacBio provides a tarball with GRCh38 reference files required for tertiary analyses [^3].

Can create `pbsv_splits.json` using script `make_chrom_splits_json.py` or use file in the PacBio reference data tarball[^3].

#### CHM13

Reference genome and trf bed file downloaded using bash script `https://raw.githubusercontent.com/PacificBiosciences/reference_genomes/main/reference_genomes/human_chm13v2p0_maskedY_rCRS/human_chm13v2p0_maskedY_rCRS.sh`
Bash script from `https://github.com/PacificBiosciences/reference_genomes`, git repo.
Script using samtools faidx to index the reference. 


Using command from GRCh38 resources readme (modified for CHM13)
`cut -f1,2 human_chm13v2p0_maskedY_rCRS.fasta.fai > human_chm13v2p0_maskedY_rCRS.chr_lengths.txt`

copied GRCh38 file and manually removed additional contigs
File in reference data bundle available at: https://zenodo.org/record/8415406

### Example Pipeline Run

How ND Olson ran pipeline on HG008 HiFi Revio data received 1/25/2024.

Using `/wrk/nolson` to run pipeline, note that inactivate files are removed from `wrk` after 90 days.  

1. Created directory for analysis `mkdir pacbio-hifi-20240125-HG008`
1. Copied `hifi_reads`(unaligned bams) to directory from workstation using rsync to subdirectory `pacbio-hifi-20240125-HG008/PacBio_Revio_20240125`
1. starting tmux `tmux new-session -t hifi`
1. activating mamba env `micromamba activate` (note I installed `miniwdl` and `singularity` in my base environment, this is not best practices)
1. Completed `input.json` file see GRCh38 file below.
1. Starting GRCh38 pipeline run

```sh
miniwdl run ../HiFi-human-WGS-WDL/workflows/main.wdl \
    -i HG008_GRCh38_inputs.json \
    -d analysis/GRCh38/
```

Pipeline run takes about a day, due to user resource limits. These might be different for other users and can potentially ask admin for increased limits.

#### Example Input JSON File

```json
{
  "humanwgs.cohort": {
    "cohort_id": "HG008",
    "samples": [
      {
        "sample_id": "HG008-T",
        "movie_bams": [
          "/wrk/nolson/pacbio-hifi-20240125-HG008/PacBio_Revio_20240125/HG008-T/HG008-T_HiFi-Revio_m84039_240113_032943_s4.hifi_reads.bc2005.bam",
          "/wrk/nolson/pacbio-hifi-20240125-HG008/PacBio_Revio_20240125/HG008-T/HG008-T_HiFi-Revio_m84039_240114_012401_s1.hifi_reads.bc2005.bam"
        ],
        "sex": "FEMALE",
        "affected": false
      },
      {
        "sample_id": "HG008-N-P",
        "movie_bams": [
          "/wrk/nolson/pacbio-hifi-20240125-HG008/PacBio_Revio_20240125/HG008-N-P/HG008-N-P_HiFi-Revio_m84039_240114_032308_s2.hifi_reads.bc2006.bam"
        ],
        "sex": "FEMALE",
        "affected": false
      }
    ],
    "phenotypes": [
      "HP:0000001"
    ]
  },
  "humanwgs.reference": {
    "name": "GRCh38",
    "fasta": {
      "data": "/wrk/nolson/dataset/GRCh38/GRCh38_GIABv3_no_alt_analysis_set_maskedGRC_decoys_MAP2K3_KMT2C_KCNJ18.fasta",
      "data_index": "/wrk/nolson/dataset/GRCh38/GRCh38_GIABv3_no_alt_analysis_set_maskedGRC_decoys_MAP2K3_KMT2C_KCNJ18.fasta.fai"
    },
    "pbsv_splits": "/wrk/nolson/dataset/GRCh38/GRCh38_GIABv3_no_alt_analysis_set_maskedGRC_decoys_MAP2K3_KMT2C_KCNJ18.pbsv_splits.json",
    "tandem_repeat_bed": "/wrk/nolson/dataset/GRCh38/human_GRCh38_no_alt_analysis_set.trf.bed",
    "trgt_tandem_repeat_bed": "/wrk/nolson/dataset/GRCh38/trgt/human_GRCh38_no_alt_analysis_set.trgt.v0.3.4.bed",
    "hificnv_exclude_bed": {
      "data": "/wrk/nolson/dataset/GRCh38/hificnv/cnv.excluded_regions.common_50.hg38.bed.gz",
      "data_index": "/wrk/nolson/dataset/GRCh38/hificnv/cnv.excluded_regions.common_50.hg38.bed.gz.tbi"
    },
    "hificnv_expected_bed_male": "/wrk/nolson/dataset/GRCh38/hificnv/expected_cn.hg38.XY.bed",
    "hificnv_expected_bed_female": "/wrk/nolson/dataset/GRCh38/hificnv/expected_cn.hg38.XX.bed"
  },
  "humanwgs.backend": "HPC",
  "humanwgs.preemptible": false
}
```

## Footnotes

[^1:] For GRCh37 and CHM13 the following tasks were commented out `hificnv`, `coverage_dropouts`, and `trgt`. `paraphrase` was modified to run conditionally based on reference name. May eventually modify `hificnv`, `coverage_dropouts`, and `trgt` to similarly run conditionally.

[^2:] As of 2/7 not sure the gff reference files are used with the modified version of the pipeline. 

[^3:] Reference data is hosted on Zenodo at [10.5281/zenodo.8415406](https://zenodo.org/record/8415406).  Download the reference data bundle and extract it to a location on your HPC, then update the input template file with the path to the reference data.

[^4:] See PacBio WDL backend HPC documentation for additional information, [https://github.com/PacificBiosciences/HiFi-human-WGS-WDL/tree/main/backends/hpc](https://github.com/PacificBiosciences/HiFi-human-WGS-WDL/tree/main/backends/hpc)

[^5:] NDO modified `[slurm]` section to `extra_args="--partition batch --comment 'run with miniwdl' --time=3-00:00:00"`, for nisaba, not sure modification necessary but without the `--time` the pipeline was failing for me.

[^6:] NDO using absolute paths, relative paths better for reproducibility but I was lazy and used absolute paths when I was just trying to get the pipeline to run.