import json
import logging
import numpy as np
import os
import pandas as pd
import tqdm

from typing import List

logging.basicConfig(
  format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def log_training_dynamics(output_dir: os.path,
                          epoch: int,
                          train_ids: List[int],
                          train_logits: List[List[float]],
                          train_golds: List[int]):
  """
  Save training dynamics (logits) from given epoch as records of a `.jsonl` file.
  """
  td_df = pd.DataFrame({"guid": train_ids,
                        f"logits_epoch_{epoch}": train_logits,
                        "gold": train_golds})

  logging_dir = os.path.join(output_dir, f"training_dynamics")
  # Create directory for logging training dynamics, if it doesn't already exist.
  if not os.path.exists(logging_dir):
    os.makedirs(logging_dir)
  epoch_file_name = os.path.join(logging_dir, f"dynamics_epoch_{epoch}.jsonl")
  # Log training dynamics in epoch file: Create if not present else read, concatenate and write again
  if not os.path.exists(epoch_file_name):
      td_df.to_json(epoch_file_name, lines=True, orient="records")
  else:
      f=pd.read_json(epoch_file_name, orient="records", lines=True)
      td_df=pd.concat((f, td_df), axis=0)
      td_df.to_json(epoch_file_name, orient="records", lines=True)
  logger.info(f"Training Dynamics logged to {epoch_file_name}")

def log_eval_dynamics(output_dir: os.path,
                          epoch: int,
                          eval_ids: List[int],
                          eval_logits: List[List[float]],
                          eval_golds: List[int]):
  """
  Save Evaluation dynamics (logits) from given epoch as records of a `.jsonl` file.
  """
  td_df = pd.DataFrame({"guid": eval_ids,
                        f"logits_epoch_{epoch}": eval_logits,
                        "gold": eval_golds})

  logging_dir = os.path.join(output_dir, f"eval_dynamics")
  # Create directory for logging training dynamics, if it doesn't already exist.
  if not os.path.exists(logging_dir):
    os.makedirs(logging_dir)
  epoch_file_name = os.path.join(logging_dir, f"dynamics_epoch_{epoch}.jsonl")
  # Log eval dynamics in epoch file: Create if not present else read, concatenate and write again
  if not os.path.exists(epoch_file_name):
      td_df.to_json(epoch_file_name, lines=True, orient="records")
  else:
      f=pd.read_json(epoch_file_name, orient="records", lines=True)
      td_df=pd.concat((f, td_df), axis=0)
      td_df.to_json(epoch_file_name, orient="records", lines=True)
  logger.info(f"Eval Dynamics logged to {epoch_file_name}")

def read_training_dynamics(model_dir: os.path,
                           strip_last: bool = False,
                           id_field: str = "guid",
                           burn_out: int = None):
  """
  Given path to logged training dynamics, merge stats across epochs.
  Returns:
  - Dict between ID of a train instances and its gold label, and the list of logits across epochs.
  """
  train_dynamics = {}

  td_dir = os.path.join(model_dir, "training_dynamics")
  num_epochs = len([f for f in os.listdir(td_dir) if os.path.isfile(os.path.join(td_dir, f))])
  if burn_out:
    num_epochs = burn_out

  logger.info(f"Reading {num_epochs} files from {td_dir} ...")
  for epoch_num in tqdm.tqdm(range(num_epochs)):
    epoch_file = os.path.join(td_dir, f"dynamics_epoch_{epoch_num}.jsonl")
    assert os.path.exists(epoch_file)

    with open(epoch_file, "r") as infile:
      for line in infile:
        record = json.loads(line.strip())
        guid = record[id_field] if not strip_last else record[id_field][:-1]
        if guid not in train_dynamics:
          assert epoch_num == 0
          train_dynamics[guid] = {"gold": record["gold"], "logits": []}
        train_dynamics[guid]["logits"].append(record[f"logits_epoch_{epoch_num}"])

  logger.info(f"Read training dynamics for {len(train_dynamics)} train instances.")
  return train_dynamics

def read_eval_dynamics(model_dir: os.path,
                           strip_last: bool = False,
                           id_field: str = "guid",
                           burn_out: int = None):
  """
  Given path to logged eval dynamics, merge stats across epochs.
  Returns:
  - Dict between ID of a eval instances and its gold label, and the list of logits across epochs.
  """
  eval_dynamics = {}

  td_dir = os.path.join(model_dir, "eval_dynamics")
  num_epochs = len([f for f in os.listdir(td_dir) if os.path.isfile(os.path.join(td_dir, f))])
  if burn_out:
    num_epochs = burn_out

  logger.info(f"Reading {num_epochs} files from {td_dir} ...")
  for epoch_num in tqdm.tqdm(range(num_epochs)):
    epoch_file = os.path.join(td_dir, f"dynamics_epoch_{epoch_num}.jsonl")
    assert os.path.exists(epoch_file)

    with open(epoch_file, "r") as infile:
      for line in infile:
        record = json.loads(line.strip())
        guid = record[id_field] if not strip_last else record[id_field][:-1]
        if guid not in eval_dynamics:
          assert epoch_num == 0
          eval_dynamics[guid] = {"gold": record["gold"], "logits": []}
        eval_dynamics[guid]["logits"].append(record[f"logits_epoch_{epoch_num}"])

  logger.info(f"Read eval dynamics for {len(eval_dynamics)} eval instances.")
  return eval_dynamics
