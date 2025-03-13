# RotaFinder
## About
WARNING: This command line tool for genotyping of Rotavirus A is currently being validated for G and P-typing. It may be prone to errors, escpecially for other than G/P-typing. 

This is a pipeline for genotyping Rotavirus A from Illumina MiSeq raw data. SPAdes is run with several parameters and contigs with length above 500 and coverage above 3 are considered. Genotyping is performed by blast and local database. Cutoffs are applied as described by https://pubmed.ncbi.nlm.nih.gov/18604469/. 

## Install

You will need conda. Dependencies are described in env.yaml and can be installed with 

```
conda env create -f env.yaml
```


## Use

The script will loop through folders one level down from where it is called and expects one folder per sample. In each folder it expects the files **_R1_001.fastq.gz* and **_R2_001.fastq.gz*.

```
bash path\to\RotaFinder.sh
```

## Output

Summary file "Labware.csv" with the conclusions for all samples. If a gene is not found the genotype will be "X". If several genotypes of one gene is found in the same sample the script will output the one with the most full sequences. If a tie, there will be "?" instead of a number. The column "Extra Information" will contain information about genotypes if more than one is detected. If closest reference is >G1|LC822561.1/Vaccine/USA/RIX4414/1988 and/or >P8|LC822559.1/Vaccine/USA/RIX4414/1988 the output will also include percentage similarity to reference. More details are generated in the sample folders, including fasta sequences after deNovo assembly. 

The validated version of the script is version 1 (see releases). The main repo contains updates.

# NGS Bioinformatics Pipeline


```mermaid
graph TD;
    Trimmomatic["Trimmomatic (Adapter Trimming and Quality Control)"];

    Clumpify_Spades["Deduplicate with Clumpify + rnaViralSPAdes"];
    BBNorm_Spades1["BBnorm (100x) + rnaViralSPAdes"];
    BBNorm_Spades2["BBnorm (500x) + rnaViralSPAdes"];
    RNAviralSPAdes["RNAviralSPAdes"];
    SPAdes["SPAdes --isolate"];

    BLAST["BLAST"];
    REDUCE["Discard contigs with k-mer coverage <= 3, and length <= 500"];
    Report["REPORT"];

    Trimmomatic --> Clumpify_Spades;
    Trimmomatic --> BBNorm_Spades1;
    Trimmomatic --> BBNorm_Spades2;
    Trimmomatic --> RNAviralSPAdes;
    Trimmomatic --> SPAdes;

    Clumpify_Spades --> REDUCE;
    BBNorm_Spades1 --> REDUCE;
    BBNorm_Spades2 --> REDUCE;
    RNAviralSPAdes --> REDUCE;
    SPAdes --> REDUCE;

    REDUCE --> BLAST

    BLAST --> |"Extract genotype and percentage similarity, apply cut-off"| Report;
