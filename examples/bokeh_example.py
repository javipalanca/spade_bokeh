import getpass

from spade import agent

import spade_bokeh

from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure

from bokeh.sampledata.sea_surface_temperature import sea_surface_temperature


class MyBokehAgent(spade_bokeh.BokehServerMixin, agent.Agent):

    async def controller(self, request):
        script = self.bokeh_server.get_plot_script("/my_plot")

        return {"script": script}

    async def setup(self):

        self.web.add_get("/plot", self.controller, "plot.html")

        self.web.start(port=10000)
        self.bokeh_server.start()

        self.bokeh_server.add_plot("/my_plot", self.modify_doc)

    def modify_doc(self, doc):
        df = sea_surface_temperature.copy()
        source = ColumnDataSource(data=df)

        plot = figure(x_axis_type='datetime', y_range=(0, 25), y_axis_label='Temperature (Celsius)',
                      title="Sea Surface Temperature at 43.18, -70.43")
        plot.line('time', 'temperature', source=source)

        def callback(attr, old, new):
            if new == 0:
                data = df
            else:
                data = df.rolling('{0}D'.format(new)).mean()
            source.data = ColumnDataSource(data=data).data

        slider = Slider(start=0, end=30, value=0, step=1, title="Smoothing by N Days")
        slider.on_change('value', callback)

        doc.add_root(column(slider, plot))


if __name__ == "__main__":

    jid = input("Agent JID> ")
    passwd = getpass.getpass()
    a = MyBokehAgent(jid, passwd)
    a.start()
