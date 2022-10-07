import math
import os

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

START_ANGLE = -180


def get_new_coordinate(x0, y0, length, angle):
    """
    Take last coordinate plus new length and angle in order to calculate new coordinate
    :param x0: last x coordinate
    :param y0: last y coordinate
    :param length: length of line
    :param angle: angle of line
    :return: new coordinate
    """
    x1 = x0 + math.cos(math.radians(angle)) * length
    y1 = y0 + math.sin(math.radians(angle)) * length
    return x1, y1


def calculate_coordinates(datatable):
    # Coordinates DataFrame has one additional line = starting point (0,0)
    coordinates = pd.DataFrame(np.zeros(shape=(datatable.shape[0] + 1, datatable.shape[1])), columns=["x", "y"])

    for index, row in datatable.iterrows():
        angle = (START_ANGLE + 180 + row[1]) % 360  # Convert relative angle to absolute angle
        x, y = get_new_coordinate(x0=coordinates.iloc[index, 0],
                                  y0=coordinates.iloc[index, 1],
                                  length=row[0],
                                  angle=angle)
        coordinates.iloc[index + 1, 0] = x
        coordinates.iloc[index + 1, 1] = y

    """
    Plausibility check: is the distance between first and last coordinate roughly the same?
    In other words: is the room closed? ;-)
    """
    print("Distance between start and end point [in cm]:")
    x = math.pow(coordinates.iloc[0, 0] - coordinates.iloc[-1, 0], 2)
    y = math.pow(coordinates.iloc[0, 1] - coordinates.iloc[-1, 1], 2)
    print(math.sqrt(x + y))

    return coordinates


def plot_room(coordinates, raw_table, room_name):
    length_x = coordinates["x"].max() - coordinates["x"].min()
    length_y = coordinates["y"].max() - coordinates["y"].min()

    fig, ax = plt.subplots(figsize=(int(length_x / 15), int(length_y / 15)))
    for i in range(coordinates.shape[0] - 1):
        two_coordinates = coordinates.iloc[i:i + 2, :]
        ax = two_coordinates.plot(ax=ax, kind="line", marker="o", x="x", y="y", c="black", legend=None)

        # Label the drawn line in the center
        x_mean = two_coordinates["x"].mean()
        y_mean = two_coordinates["y"].mean()
        plt.annotate(str(raw_table.iloc[i, 0]) + "cm",  # this is the text (number of cm)
                     (x_mean, y_mean),  # this is the point to label
                     textcoords="offset points",  # how to position the text
                     xytext=(5, 5),  # distance from text to points (x,y)
                     ha="center",
                     fontsize=int(length_x / 20))

    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.xaxis.set_major_locator(ticker.MultipleLocator(100))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(100))
    plt.title(str(room_name), fontsize=int(length_x / 10))
    ax.tick_params(labelsize=int(length_x / 40))
    plt.grid(True)
    plt.savefig("Output/" + str(room_name) + ".png")


def process_room(file_name):
    room_name = file_name.split(".")[0]
    print(f"Process room: {room_name}")
    raw_table = pd.read_csv("Input/" + file_name, sep=";")

    coordinates = calculate_coordinates(raw_table)

    plot_room(coordinates, raw_table, room_name)


if __name__ == "__main__":
    for file_name in os.listdir("Input"):
        process_room(file_name)
