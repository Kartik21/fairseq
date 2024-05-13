#!/usr/bin/env python
# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import contextlib
import sys

import sentencepiece as spm


def encode(inputs, outputs, model, output_format="piece", min_len=None, max_len=None):
    
    '''
    model: sentencepiece model to use for encoding
    input: input files to filter/encode
    output: path to save encoded outputs
    output_format: piece or id
    min_len: filter sentence pairs with fewer than N tokens
    max_len: filter sentence pairs with more than N tokens
    '''

    '''
     parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model", required=True, help="sentencepiece model to use for encoding"
    )
    parser.add_argument(
        "--inputs", nargs="+", default=["-"], help="input files to filter/encode"
    )
    parser.add_argument(
        "--outputs", nargs="+", default=["-"], help="path to save encoded outputs"
    )
    parser.add_argument("--output_format", choices=["piece", "id"], default="piece")
    parser.add_argument(
        "--min-len",
        type=int,
        metavar="N",
        help="filter sentence pairs with fewer than N tokens",
    )
    parser.add_argument(
        "--max-len",
        type=int,
        metavar="N",
        help="filter sentence pairs with more than N tokens",
    )
    args = parser.parse_args()
    
    '''
   

    assert len(inputs) == len(
        outputs
    ), "number of input and output paths should match"

    sp = spm.SentencePieceProcessor()
    sp.Load(model)

    if output_format == "piece":

        def encode(input):
            return sp.EncodeAsPieces(input)

    elif output_format == "id":

        def encode(input):
            return list(map(str, sp.EncodeAsIds(input)))

    else:
        raise NotImplementedError

    if min_len is not None or max_len is not None:

        def valid(line):
            return (min_len is None or len(line) >= min_len) and (
                max_len is None or len(line) <= max_len
            )

    else:

        def valid(lines):
            return True

    with contextlib.ExitStack() as stack:
        inputs = [
            stack.enter_context(open(input, "r", encoding="utf-8"))
            if input != "-"
            else sys.stdin
            for input in inputs
        ]
        outputs = [
            stack.enter_context(open(output, "w", encoding="utf-8"))
            if output != "-"
            else sys.stdout
            for output in outputs
        ]

        stats = {
            "num_empty": 0,
            "num_filtered": 0,
        }

        def encode_line(line):
            line = line.strip()
            if len(line) > 0:
                line = encode(line)
                if valid(line):
                    return line
                else:
                    stats["num_filtered"] += 1
            else:
                stats["num_empty"] += 1
            return None

        for i, lines in enumerate(zip(*inputs), start=1):
            enc_lines = list(map(encode_line, lines))
            if not any(enc_line is None for enc_line in enc_lines):
                for enc_line, output_h in zip(enc_lines, outputs):
                    print(" ".join(enc_line), file=output_h)
            if i % 10000 == 0:
                print("processed {} lines".format(i), file=sys.stderr)

        print("skipped {} empty lines".format(stats["num_empty"]), file=sys.stderr)
        print("filtered {} lines".format(stats["num_filtered"]), file=sys.stderr)



