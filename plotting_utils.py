import matplotlib.pyplot as plt

plt.style.use('fivethirtyeight')


def stacked_bar_plot(
    fig, ax, xlabels, y1, y2, ax_i, ylabel: str = None, title: str = None
):
    """
    Parameters
    ----------
    xlabels
    y1
    y2
    legend_labels
    ylabel : str
    title : str
    """
    # fig = plt.figure(facecolor='white')
    # ax = plt.axes()

    ax.flat[ax_i].bar(xlabels, y1, color='gray')
    ax.flat[ax_i].bar(xlabels, y2, bottom=y1, color='salmon')

    if ylabel:
        ax.flat[ax_i].set_ylabel(ylabel)
    if title:
        ax.flat[ax_i].set_title(title)
    ax.flat[ax_i].legend()

    return fig, ax
