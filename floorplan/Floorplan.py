import numpy as np
import math
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os


def get_coordinates(x0, y0, length, angle):
    x1 = x0 + math.cos(math.radians(angle)) * length
    y1 = y0 + math.sin(math.radians(angle)) * length
    return x1, y1


def calculate_room(f):
    room_name = f.split('.')[0]
    datatable = pd.read_csv('Input/' + f, sep=';')

    # Output is one line longer: in the first line there is only the starting point [0,0]
    output = pd.DataFrame(np.zeros(shape=(datatable.shape[0] + 1, datatable.shape[1])), columns=['x', 'y'])

    angle = -180
    for index, row in datatable.iterrows():
        """
        Convert relative angle to absolute angle
        """
        # print('relative angle: ' + str(row[1]))
        angle = (angle + 180 + row[1]) % 360
        # print('absolute angle: ' + str(angle))
        """
        Take last coordinate plus new length and angle in order to calculate new coordinate
        """
        x, y = get_coordinates(output.iloc[index, 0], output.iloc[index, 1], row[0], angle)
        # print('x: ' + str(x))
        # print('y: ' + str(y))
        # Set x coordinate
        output.iloc[index + 1, 0] = x
        # Set y coordinate
        output.iloc[index + 1, 1] = y

    """
    Plausibility check: is the distance between first and last coordinate roughly the same?
    In other words: is the room closed? ;-)
    """
    print('Distance between start and end point [in cm]:')
    print(math.sqrt(
        math.pow(output.iloc[0, 0] - output.iloc[-1, 0], 2) + math.pow(output.iloc[0, 1] - output.iloc[-1, 1], 2)))

    length_x = output['x'].max() - output['x'].min()
    length_y = output['y'].max() - output['y'].min()

    fig, ax = plt.subplots(figsize=(int(length_x / 15), int(length_y / 15)))
    for i in range(output.shape[0] - 1):
        extract = output.iloc[i:i + 2, :]
        ax = extract.plot(ax=ax, kind='line', marker='o', x='x', y='y', c='black', legend=None)

        x_co = extract['x'].mean()
        y_co = extract['y'].mean()

        # Calculate center of line
        plt.annotate(str(datatable.iloc[i, 0]) + 'cm',  # this is the text
                     (x_co, y_co),  # this is the point to label
                     textcoords="offset points",  # how to position the text
                     xytext=(5, 5),  # distance from text to points (x,y)
                     ha='center', fontsize=int(length_x / 20))

    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.xaxis.set_major_locator(ticker.MultipleLocator(100))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(100))
    plt.title(str(room_name), fontsize=int(length_x / 10))
    ax.tick_params(labelsize=int(length_x / 40))
    plt.grid(True)
    plt.savefig('Output/' + str(room_name) + '.png')


if __name__ == "__main__":
    # Read Data from CSV files
    for f in os.listdir('Input'):
        calculate_room(f)
