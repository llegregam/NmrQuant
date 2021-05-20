from abc import ABC, abstractmethod
from itertools import cycle

import matplotlib.pyplot as plt
import numpy as np
import colorcet as cc
from natsort import natsorted
from ordered_set import OrderedSet

class Colors:
    """Color component class for the different plotting classes"""

    IndHistA_colors = cc.glasbey_bw[:]

    IndLineA_colors = {"grey_scale" : cc.CET_L1, "red_to_yellow" : cc.CET_L3, "blue_scale" : cc.CET_L6,
                       "green_scale" : cc.CET_L14, "darkred_scale" : cc.CET_L13}

    @staticmethod
    def IndLineA_colorgen(seq_numbs, color_numbs):

        result = [] # Where colormaps will be stored

        colormaps = list(Colors.IndLineA_colors.items()) # Get the maps
        colormap_cycler = cycle(colormaps) # Make a cycler to avoid Index errors

        for ind, i in enumerate(colormap_cycler):
            color_list = []
            if ind < seq_numbs: # since it starts at 0, if equal then we have gone through the sequence count
                colors = i[1]
                # Divide by the number of requested colors to get evenly spaced colors. Substract 1/10th from the color
                # list to avoid getting the last value which is sometimes too white and invisible
                div = int((len(colors) - int((len(colors)/10)))/color_numbs)

                for x in range(1, color_numbs+1):
                    color_list.append(colors[x*div])
                result.append(color_list)
            else:
                break

        return result

    @staticmethod
    def IndHistB_colorgen(conditions_list):
        colorlist = []

        for ind, condition in enumerate(OrderedSet(conditions_list)):
            color = cc.glasbey_bw[ind]
            x = conditions_list.count(condition)
            for i in range(x):
                colorlist.append(color)
        return colorlist

class HistPlot(ABC):

    def __init__(self, metabolite, input_data):

        self.data = input_data

        if "# Spectrum#" in input_data.index.names:
            self.data = self.data.droplevel("# Spectrum#")

        if "# Spectrum#" in input_data.columns:
            self.data = self.data.drop("# Spectrum#", axis=1)

        if "Conditions" not in self.data.index.names:
            raise IndexError("Conditions column not found in index")

        if "Time_Points" in self.data.index.names:
            if len(self.data.index.get_level_values("Time_points").unique()) > 1:
                raise IndexError("Data should not contain more than one time point")
            else:
                self.data.droplevel("Time_Points")

        self.metabolite = metabolite

        self.x_labels = list(self.data.index)
        self.x_ticks = np.arange(1, 1 + len(self.x_labels))
        self.y = self.data[self.metabolite].values

    def __repr__(self):

        return f"Metabolite = {self.metabolite}\n" \
               f"x_labels = {list(self.x_labels)}\n" \
               f"y = {self.y}\n" \
               f"x_ticks = {self.x_ticks}"

    def __call__(self):

        fig = self._build_plot()

        return fig

    @abstractmethod
    def _build_plot(self):
        pass


class IndHistA(HistPlot):
    """Class for histogram with one or more conditions, no replicates and one or no time points"""

    def __init__(self, input_data, metabolite):

        super().__init__(input_data, metabolite)

        self.colors = Colors.IndHistA_colors

        if "Replicates" in self.data.index.names:
            if len(self.data.index.get_level_values("Replicates").unique()) > 1:
                raise IndexError("Data should not contain more than one replicate")
            else:
                self.data.droplevel("Replicates")

    def _build_plot(self):

        fig, ax = plt.subplots()

        ax.bar(self.x_ticks, self.y, color=self.colors)
        ax.set_xticks(self.x_ticks)
        ax.set_xticklabels(self.x_labels, rotation=45, ha="right", rotation_mode="anchor")
        ax.set_title(self.metabolite)

        fig.tight_layout()

        return fig

class IndHistB(HistPlot):

    def __init__(self, input_data, metabolite):

        super().__init__(input_data, metabolite)

        for i in ["Conditions", "Replicates"]:
            if i not in self.data.index.names:
                raise KeyError(f"{i} is missing from index")

        self.data = self.data.reindex(natsorted(self.data.index))
        self.x_labels = list(self.data.index)
        self.x_ticks = np.arange(1, 1 + len(self.x_labels))

        try:
            self.colors = Colors.IndHistB_colorgen(list(self.data.index.get_level_values("Conditions")))
        except KeyError:
            self.colors = Colors.IndHistB_colorgen(list(self.data.Conditions.values))
        except Exception as e:
            raise RuntimeError(f"Error while retrieving condition list for color generation. Traceback: {e}")


class MultHistB(HistPlot):

    def __init__(self, metabolite, input_data, std_data ):

        super().__init__(metabolite, input_data)

        self.data = input_data
        self.stds = std_data
        self.yerr = self.stds[self.metabolite].values

        if "Time_Points" in self.data.index.names:
            self.data = self.data.droplevel("Time_Points")

        try:
            self.colors = Colors.IndHistB_colorgen(list(self.data.index.get_level_values("Conditions")))
        except KeyError:
            self.colors = Colors.IndHistB_colorgen(list(self.data.Conditions.values))
        except Exception as e:
            raise RuntimeError(f"Error while retrieving condition list for color generation. Traceback: {e}")


    def _build_plot(self):

        fig, ax = plt.subplots()

        ax.bar(self.x_ticks, self.y, color=self.colors, yerr=self.yerr)
        ax.set_xticks(self.x_ticks)
        ax.set_xticklabels(self.x_labels, rotation=45, ha="right", rotation_mode="anchor")
        ax.set_title(self.metabolite)

        fig.tight_layout()

        return fig


class LinePlot(ABC):

    def __init__(self, metabolite, input_data, display=False):

        self.metabolite = metabolite
        self.data = input_data
        self.data = self.data.loc[:, metabolite]
        self.display = display

        for i in ["Conditions", "Time_Points"]:
            if i not in self.data.index.names:
                raise IndexError(f"{i} not found in index")

        if "# Spectrum#" in input_data.index.names:
            self.data = self.data.droplevel("# Spectrum#")

        if "# Spectrum#" in input_data.columns:
            self.data = self.data.drop("# Spectrum#", axis=1)

    def __call__(self):

        fig = self._build_plot()

        return fig

    @staticmethod
    def show_figure(fig):
        # create a dummy figure and use its
        # manager to display saved fig
        dummy = plt.figure()
        new_manager = dummy.canvas.manager
        new_manager.canvas.figure = fig
        fig.set_canvas(new_manager.canvas)

    @abstractmethod
    def _build_plot(self):
        pass


class IndLine(LinePlot):

    def __init__(self, metabolite, input_data, display):

        super().__init__(metabolite, input_data, display)

        if "Replicates" not in self.data.index.names:
            raise IndexError("Replicates column not found in index")

        self.conditions = self.data.index.get_level_values("Conditions").unique()
        self.data = self.data.reorder_levels([0, 2, 1])
        self.dicts = {}

        for condition in self.conditions:
            df = self.data.loc[condition]
            repdict = {}

            for rep in df.index.get_level_values("Replicates"):
                df2 = df.loc[rep, :]
                repdict.update({rep : {"Times" : list(df2.index.get_level_values("Time_Points")),
                                       "Values" : list(df2.values)}
                                })

            self.dicts.update({condition : repdict})

    def __repr__(self):
        return f"Plotting data: {self.dicts}"

    def _build_plot(self):

        figures = []

        max_number_reps = max([max(self.dicts[i].keys()) for i in self.dicts.keys()])
        colorlist = Colors.IndLineA_colorgen(len(self.conditions), max_number_reps)

        for (i, condition), c in zip(enumerate(self.conditions), colorlist):
            fig, ax = plt.subplots()

            for rep, color in zip(self.dicts[condition].keys(), c):
                x = self.dicts[condition][rep]["Times"]
                y = self.dicts[condition][rep]["Values"]

                ax.plot(x, y, color=color, label=f"Replicate {rep}")

            ax.set_title(f"{self.metabolite}\n{condition}")
            ax.set_ylabel("Concentration in mM")
            ax.set_xlabel("Time in hours")
            ax.legend()

            fname = f"{self.metabolite}_{condition}"

            if self.display:
                fig.show()

            figures.append((fname, fig))

        if not self.display:
            return figures

















