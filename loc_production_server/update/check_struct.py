from __future__ import annotations
import argparse
import numpy as np


def data_coord_extraction(
    target_pdb_file: str, identfier: str = "ATOM"
) -> tuple[
    np.ndarray[tuple[int, int], np.dtype[str]],
    np.ndarray[tuple[int, int], np.dtype[float]],
    np.ndarray[tuple[int], np.dtype[float]],
]:
    """extracts the coordinates and the residue data from a pdb file
    :parameter
         - target_pdb_file:
           path to pdb file for protein of interest
         - identifier
    :returns
         - res_coords:
           contains coordinates of corresponding residues to the new_data
           entries
    """
    res_coords = []
    # reading the pdb file
    with open(target_pdb_file, "r") as pfile:
        for line in pfile:
            if identfier in line[:6]:
                line = line.strip()
                res_coords.append(
                    [line[31:39].strip(), line[39:47].strip(), line[47:55].strip()]
                )

    res_coords = np.asarray(res_coords, dtype=float)
    return res_coords


def shift(
    arr: np.ndarray[tuple[int, int], np.dtype[int]],
) -> tuple[
    np.ndarray[tuple[int], np.dtype[int | float]],
    np.ndarray[tuple[int, int], np.dtype[int | float]],
]:
    """shift coordinated based on the shift of their centroid to the origin
    :parameter
        - arr:
          the array of coordinates to be shifted
    :return
        - centroid
          the centroid of the array
        - arr_shifted
          the shifted array
    """
    centroid = np.mean(arr, axis=0)
    arr_shifted = arr - centroid
    return centroid, arr_shifted


def rotamat(
    system1: np.ndarray[tuple[int, int], np.dtype[int]],
    system2: np.ndarray[tuple[int, int], np.dtype[int]],
) -> tuple[
    np.ndarray[tuple[int], np.dtype[int | float]],
    np.ndarray[tuple[int], np.dtype[int | float]],
    np.ndarray[tuple[int, int], np.dtype[int]],
]:
    """kabsch algorithm to find the optimal rotation matrix
    :parameter
        - system1, system2:
          coordinate systems for which the optimal alignment should be calculated
    :return
        - U:
          the rotation matrix
        - c_s1, c_s2:
          centroids of each system
    """
    # shift the coordinates to the origin
    c_s1, system1 = shift(system1)
    c_s2, system2 = shift(system2)

    # covariance matrix
    cov_mat = np.dot(np.transpose(system1), system2)
    # singular value decomposition
    V, S, W = np.linalg.svd(cov_mat)

    # check for right-handedness of the coordinate system
    d = (np.linalg.det(V) * np.linalg.det(W)) < 0.0
    if d:
        S[-1] = -S[-1]
        V[:, -1] = -V[:, -1]

    # create Rotation matrix U
    U = np.dot(V, W)
    return c_s1, c_s2, U


def absolute_deviation(
    c0: np.ndarray[tuple[int, int], np.dtype[float]],
    c1: np.ndarray[tuple[int, int], np.dtype[float]],
):
    """
    mean absolute deviation
    """
    return (np.abs(c0 - c1)).sum(axis=1).mean()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-o",
        "--old",
        type=str,
        required=True,
        help="path to pdb file containing the old prediction",
    )
    parser.add_argument(
        "-n",
        "--new",
        type=str,
        required=True,
        help="path to pdb file containing the new prediction",
    )
    args = parser.parse_args()
    coord0 = data_coord_extraction(args.old)
    coord1 = data_coord_extraction(args.new)
    c0, c1, rmat = rotamat(coord0, coord1)
    c1_moved = (rmat @ (coord1 - c1).T).T + c0
    print(absolute_deviation(coord0, c1_moved)) 
