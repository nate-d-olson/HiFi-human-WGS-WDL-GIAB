#!/usr/bin/env python
"""
Generating chromosome splits json file from fasta index

This script reads sequences from a FASTA file, groups them based on a specified threshold
or number of groups, and saves the grouped sequences in a JSON file.

Usage:
    python make_chrom_splits_json.py input.fasta output.json [--threshold THRESHOLD] [--num-groups NUM_GROUPS]

Arguments:
    input.fasta     Path to the input FASTA file.
    output.json     Path to the output JSON file.

Options:
    --threshold THRESHOLD   Maximum total length of sequences in a group (default: 10000000).
    --num-groups NUM_GROUPS Number of groups for grouping (default: None, uses threshold method).

Example:
    python make_chrom_splits_json.py input.fasta output.json --threshold 5000000
"""

import json
import argparse
from typing import List, Tuple

def parse_fasta_index(index_file: str) -> List[Tuple[str, int]]:
    """
    Parse a FASTA index file and return a list of tuples (sequence_name, sequence_length).

    Args:
        index_file (str): path to fasta index file.
        threshold (int): Maximum total length of sequences in a group.

    Returns:
        List[Tuple[str, int]]: List of tuples with sequence names and lengths.
    """
    sequences = []
    with open(index_file, 'r') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                sequence_name = parts[0]
                sequence_length = int(parts[1])
                sequences.append((sequence_name, sequence_length))
    return sequences

def group_sequences_by_threshold(sequences: List[Tuple[str, int]], threshold: int) -> List[List[str]]:
    """
    Group sequences by a given threshold.

    Args:
        sequences (List[Tuple[str, int]]): List of tuples with sequence names and lengths.
        threshold (int): Maximum total length of sequences in a group.

    Returns:
        List[List[str]]: List of grouped sequences.
    """

    groups = []
    current_group = []
    current_group_length = 0

    for sequence_name, sequence_length in sequences:
        if current_group_length == 0:
            current_group.append(sequence_name)
            current_group_length += sequence_length
        elif current_group_length + sequence_length <= threshold:
            current_group.append(sequence_name)
            current_group_length += sequence_length
        else:
            groups.append(current_group)
            current_group = [sequence_name]
            current_group_length = sequence_length

    if current_group:
        groups.append(current_group)

    return groups

def group_sequences_by_number(sequences: List[Tuple[str, int]], num_groups: int) -> List[List[str]]:
    """
    Group sequences into a given number of groups.

    Args:
        sequences (List[Tuple[str, int]]): List of tuples with sequence names and lengths.
        num_groups (int): Number of groups to create.

    Returns:
        List[List[str]]: List of grouped sequences.
    """

    groups = [[] for _ in range(num_groups)]
    total_length = sum(sequence_length for _, sequence_length in sequences)
    group_length = total_length // num_groups

    current_group_index = 0
    current_group_length = 0

    for sequence_name, sequence_length in sequences:
        if current_group_length + sequence_length <= group_length:
            groups[current_group_index].append(sequence_name)
            current_group_length += sequence_length
        elif current_group_index == num_groups - 1:
            groups[current_group_index].append(sequence_name)
            current_group_length += sequence_length
        else:
            current_group_index += 1
            groups[current_group_index].append(sequence_name)
            current_group_length = sequence_length

    return groups

def main():
    """
    Main function to parse command line arguments and execute sequence grouping.
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("index_file", help="Path to the input FASTA index file")
    parser.add_argument("output_file", help="Path to the output JSON file")
    parser.add_argument("--threshold", type=int, default=10000000, help="Threshold value for grouping (default: 10000000)")
    parser.add_argument("--num-groups", type=int, default=None, help="Number of groups for grouping (default: None, uses threshold method)")

    args = parser.parse_args()

    # Parse the FASTA index file
    sequences = parse_fasta_index(args.index_file)

    if args.num_groups is None:
        groups = group_sequences_by_threshold(sequences, args.threshold)
    else:
        groups = group_sequences_by_number(sequences, args.num_groups)

    with open(args.output_file, "w") as json_file:
        json.dump(groups, json_file, indent=2)

if __name__ == "__main__":
    main()