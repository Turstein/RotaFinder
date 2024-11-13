# RotaFinder
## About

This is a pipeline for genotyping Rotavirus A from Illumina MiSeq raw data. SPAdes is run with several parameters and relevant contigs is identified by VIGOR4. Genotyping is performed by blast and local database. Cutoffs are applied as described by https://pubmed.ncbi.nlm.nih.gov/18604469/ 

## Install

You will need docker and conda. Dependencies are described in env.yaml and can be installed with 

```
conda env create -f env.yaml
```

The docker container can be built can be built from the provided directory "vigor4" with:

```
docker build -t vigor4 .
```


## Use

The script will loop through folders one level down from where it is called and expects one folder per sample. In each folder it expects the files **_R1_001.fastq.gz* and **_R2_001.fastq.gz*.

```
bash path\to\RotaFinder.sh
```

## Output

Summary file "blast_rotavar.csv" with the conclusions for all samples. If a gene is not found or several genotypes of one gene is found, there will be a "?" instead of a number. The column "Extra Information" will contain genotypes if more than one is detected. More details are provided in the sample folders, including the fasta sequences after deNovo assembly. 

# NGS Bioinformatics Pipeline

This is the pipeline used for our NGS processing:

```mermaid
graph TD;
    Trimmomatic["Trimmomatic (Quality Control)"];

    BBNorm_Spades1["BBnorm (100x) + rnaViralSPAdes"];
    BBNorm_Spades2["BBnorm (500x) + rnaViralSPAdes"];
    RNAviralSPAdes["RNAviralSPAdes"];
    SPAdes["SPAdes --isolate"];

    VIGOR4["VIGOR4 (Annotation)"];
    BLAST["BLAST"];
    Report["Extract genotype and percentage similarity, apply cut-off"];

    Trimmomatic --> BBNorm_Spades1;
    Trimmomatic --> BBNorm_Spades2;
    Trimmomatic --> RNAviralSPAdes;
    Trimmomatic --> SPAdes;

    BBNorm_Spades1 --> VIGOR4;
    BBNorm_Spades2 --> VIGOR4;
    RNAviralSPAdes --> VIGOR4;
    SPAdes --> VIGOR4;

    VIGOR4 --> |"Best Sequence Per Segment"| BLAST;

    BLAST --> Report;
