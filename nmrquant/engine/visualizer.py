import matplotlib.pyplot as plt
import numpy as np
import colorcet as cc
from natsort import natsorted
from ordered_set import OrderedSet

class Colors:

    IndHistA_colors = cc.glasbey_bw[:]

    @staticmethod
    def IndHistB_colorgen(conditions_list):
        colorlist = []

        for ind, condition in enumerate(OrderedSet(conditions_list)):
            color = cc.glasbey_bw[ind]
            x = conditions_list.count(condition)
            for i in range(x):
                colorlist.append(color)
        return colorlist


class IndHistA:

    def __init__(self, input_data, metabolite):

        self.data = input_data

        if "# Spectrum#" in input_data.index.names:
            self.data = input_data.droplevel("# Spectrum#")

        if "# Spectrum#" in input_data.columns:
            self.data = input_data.drop("# Spectrum#", axis=1)
        self.metabolite = metabolite

        self.x_labels = list(self.data.index)
        self.x_ticks = np.arange(1, 1+len(self.x_labels))
        self.y = self.data[self.metabolite].values
        self.colors = Colors.IndHistA_colors

    def __repr__(self):

        return f"Metabolite = {self.metabolite}\n" \
               f"x_labels = {list(self.x_labels)}\n" \
               f"y = {self.y}\n" \
               f"x_ticks = {self.x_ticks}"

    def __call__(self):

        fig = self._build_plot()

        return fig

    def _build_plot(self):

        fig, ax = plt.subplots()

        ax.bar(self.x_ticks, self.y, color=self.colors)
        ax.set_xticks(self.x_ticks)
        ax.set_xticklabels(self.x_labels, rotation=45, ha="right", rotation_mode="anchor")
        ax.set_title(self.metabolite)

        fig.tight_layout()

        return fig

class IndHistB(IndHistA):

    def __init__(self, input_data, metabolite):

        super(IndHistB, self).__init__(input_data, metabolite)

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





