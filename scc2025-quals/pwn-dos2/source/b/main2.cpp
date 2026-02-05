#include <iostream.h>
#include <stdio.h>

int main() {
    char line[256];

    FILE* inputFile = fopen("input.txt", "r");
    FILE* outputFile = fopen("output.txt", "w");
    
    if (!inputFile) {
        fprintf(outputFile, "Error opening input file!");
        return 1;
    }
    
    while (fscanf(inputFile, "%s", line) != EOF) {
        fprintf(outputFile, "%s\r\n", line);
    }
    
    fclose(inputFile);
    fclose(outputFile);
    
    fprintf(outputFile, "\nFile processing completed successfully!");
    
    return 0;
}