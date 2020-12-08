import sys
import os.path
import utils
from datasets import datasets

if __name__ == "__main__":
    target = sys.argv[1]
    root, _ = os.path.splitext(os.path.basename(target))
    dataset = datasets[root]
    utils.process(
        dataset["rows"](sys.argv[2]), target, dataset["fields"], dataset["rules"]
    )
