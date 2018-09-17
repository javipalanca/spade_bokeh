=====
Usage
=====

.. note:: This is a plugin for the `SPADE <https://github.com/javipalanca/spade>`_ agent platform. Please visit the
          `SPADE's documentation <https://spade-mas.readthedocs.io>`_ to know more about this platform.

Plotting figures in html usually involves too much javascript code.
To solve this there is a great python library called `Bokeh <https://bokeh.pydata.org>`_ that helps us to plot our
own figures with python code and dinamycally thanks to a server embedded with bokeh.

This plugin provides a **mixin** to include a bokeh server in an agent and to register plots to be then rendered in
your jinja2 templates of your agent's web interface.

To use SPADE Bokeh Server in a project::

    from spade import agent
    import spade_bokeh

    from bokeh.layouts import column
    from bokeh.models import ColumnDataSource, Slider
    from bokeh.plotting import figure
    from bokeh.sampledata.sea_surface_temperature import sea_surface_temperature


    class MyBokehAgent(spade_bokeh.BokehServerMixin, agent.Agent):

        # agent setup
        def setup(self):

            self.web.add_get("/plot", self.controller, "plot.html")

            self.web.start(port=10000)
            self.bokeh_server.start(hostname="localhost", port=5006)

            self.bokeh_server.add_plot("/my_plot", self.modify_doc)

        # bokeh plot creation
        def modify_doc(self, doc):
            """ here you create your plot, see the Bokeh documentation """
            df = sea_surface_temperature.copy()
            source = ColumnDataSource(data=df)

            plot = figure(x_axis_type='datetime', y_range=(0, 25),
                          y_axis_label='Temperature (Celsius)',
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

        # web controller
        async def controller(self, request):
            script = self.bokeh_server.get_plot_script("/my_plot")

            return {"script": script}



In the example below there are 3 different blocks: the agent setup, the web controller and the bokeh plot creation.


Agent setup
-----------

To activate the *spade_bokeh* plugin in your agent you must follow some steps:
    * First of all your agent needs to inherit from *spade_bokeh.BokehServerMixin*.


      .. warning:: **All the mixins** MUST be included **before** the *spade.agent.Agent class*, to respect the
                   method resolution order (e.g. ``class MyAgent(MyMixin1, MyMixin2, ..., Agent)``).


    * Next you need to start your bokeh_server with the following order: ``self.bokeh_server.start()``.
      This method may accept two arguments: the hostname and the port of the bokeh_server. By default they are
      "localhost" and 5006.

      .. warning:: Two agents can not share a same bokeh_server, so they must use different ports!


    * Finally, you can add new plots to your server using the ``add_plot`` function of bokeh_server. It accepts
      two arguments: the *path* for the plot in the bokeh server and the *callback* to build the plot.

      .. note:: You can add as many plots as you need.


Bokeh plot creation
-------------------

The method that you give to the ``add_plot`` call is the callback that will create the plot when the url path
is queried. Inside this method you can create your plot following the *Bokeh* guidelines. As in the example, the
method receives a ``doc`` argument, where the plots of your application will be rendered.

.. hint:: To learn more about how to create *Bokeh* plots please visit the `Bokeh User Guide <https://bokeh.pydata.org/en/latest/docs/user_guide.html>`_


Web controller
--------------

The final step to render your bokeh plots inside an agent view is to render the plot in a template managed by the
SPADE's web interface system.

.. hint:: Please, visit the SPADE's documentation to know more about how to create a SPADE web interface for
          your agents.

The *spade_bokeh* plugin provides you a helper function to easily render your plots inside a jinja2 template.
As in the example below, you can use the ``get_plot_script`` method with the path of the plot you want to render
and it will return you the necessary javascript to render the plot (this javascript contains the URL and necessary
code to connect to the bokeh server dinamycally).

Then you only need to render that script in your template as in the example:

.. code-block:: html

    <html lang="en">
        <head>
            <title>Bokeh Example</title>
        </head>

        <body>
            {{ script | safe}}
        </body>
    </html>

.. note:: Note that you must *safe escape* the script with the ``safe`` jinja2 filter to avoid escaping the html tags.

