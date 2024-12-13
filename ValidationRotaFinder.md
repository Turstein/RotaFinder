# NGS Bioinformatics Pipeline


```mermaid
graph TD;
    Trimmomatic["Trimmomatic (Adapter Trimming and Quality Control)"];

    BBNorm_Spades1["BBnorm (100x) + rnaViralSPAdes"];
    BBNorm_Spades2["BBnorm (500x) + rnaViralSPAdes"];
    RNAviralSPAdes["RNAviralSPAdes"];
    SPAdes["SPAdes --isolate"];

    BLAST["BLAST against reference sequences"];
    REDUCE["Discard contigs with k-mer coverage <= 3, and length <= 500"];
    Report["REPORT"];

    Trimmomatic --> BBNorm_Spades1;
    Trimmomatic --> BBNorm_Spades2;
    Trimmomatic --> RNAviralSPAdes;
    Trimmomatic --> SPAdes;

    BBNorm_Spades1 --> REDUCE;
    BBNorm_Spades2 --> REDUCE;
    RNAviralSPAdes --> REDUCE;
    SPAdes --> REDUCE;

    REDUCE --> BLAST

    BLAST --> |"Extract genotype and percentage similarity, apply cut-off"| Report;
