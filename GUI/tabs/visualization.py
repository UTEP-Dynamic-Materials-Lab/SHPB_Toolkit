from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QComboBox, QGridLayout, QPushButton, QFileDialog
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtCore import QUrl
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from rdflib import Graph, Namespace, URIRef
import os
import tempfile
import base64
from scripts.rdf_wrapper import RDFWrapper
from plotly.io import from_json
import json


class VisualizationWindow(QWidget):
    def __init__(self, file_paths):
        super().__init__()
        self.setWindowTitle("Visualization Window")
        self.setGeometry(25, 25, 1400, 900)  # Window size

        # Layouts
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # View selection layout
        view_selection_layout = QHBoxLayout()
        self.main_layout.addLayout(view_selection_layout)

        # Combo box for view selection
        view_label = QLabel("Select View Mode:")
        view_selection_layout.addWidget(view_label)

        self.view_mode_combo = QComboBox()
        self.view_mode_combo.addItems(["Single", "Dual", "Quad"])
        self.view_mode_combo.currentTextChanged.connect(self.update_layout)
        view_selection_layout.addWidget(self.view_mode_combo)

        # Multi-view layout for figures
        self.figure_layout = QGridLayout()
        self.main_layout.addLayout(self.figure_layout)

        # File paths and RDFWrapper instances
        self.file_list = file_paths
        self.experiments = [RDFWrapper(file) for file in self.file_list]
        self.experiments_test_type = []

        for file in self.experiments:
            exp_test_type = file.get_instances_of_class("dynamat:TestType")[0]
            self.experiments_test_type.append(exp_test_type)

        # Widgets for Plotly figures
        self.plot_widgets = []  # Stores web views
        self.figure_names = []  # Stores figure names
        

        # Populate figures
        self.populate_figures(1000, 600, 3, 20)        
        self.update_layout()

    def populate_figures(self, plot_width, plot_height, line_width, f_size):
        """
        Generate all figures and save them to temporary HTML files.
        """
        self.temp_files = {}  # Clear previous figure files
        self.figure_objects = {}  # Dictionary to store Plotly figures by their names

        self.sensor_signal_fig = self.create_base_figure("Strain Gauges Sensor Signals", "Time (ms)", " ",
                                                         "Strain Gauge", font_size = f_size)
        for exp in self.experiments:
            test_metadata = exp.get_instances_of_class("dynamat:Metadata")[0]
            test_name = exp.get_objects(test_metadata, "dynamat:hasTestName")[0][13:]
            x_data = self.get_series_data(exp, "dynamat:TimeSensorSignal")
            y_data = self.get_series_data(exp, "dynamat:IncidentSensorSignal")
            y_data_2 = self.get_series_data(exp, "dynamat:TransmittedSensorSignal")
            self.add_fig_data(self.sensor_signal_fig, x_data, y_data, line_width, test_name) 
            self.add_fig_data(self.sensor_signal_fig, x_data, y_data_2, line_width, test_name)
        self.save_plotly_figure(self.sensor_signal_fig, "Strain Gauge Sensors", width=plot_width, height=plot_height)

        self.extracted_signal_fig = self.create_base_figure("Extracted Pulse Signals", "Time (ms)", "Strain (mm/mm)",
                                                            "Pulse Signals", font_size = f_size)        
        for exp in self.experiments:
            test_metadata = exp.get_instances_of_class("dynamat:Metadata")[0]
            test_name = exp.get_objects(test_metadata, "dynamat:hasTestName")[0][13:]
            x_data = self.get_series_data(exp, "dynamat:TimeExtractedSignal")
            y_data = self.get_series_data(exp, "dynamat:IncidentExtractedSignal")
            y_data_2 = self.get_series_data(exp, "dynamat:TransmittedExtractedSignal")
            y_data_3 = self.get_series_data(exp, "dynamat:ReflectedExtractedSignal")
            self.add_fig_data(self.extracted_signal_fig, x_data, y_data, line_width, test_name) 
            self.add_fig_data(self.extracted_signal_fig, x_data, y_data_2, line_width, test_name)
            self.add_fig_data(self.extracted_signal_fig, x_data, y_data_3, line_width, test_name)
        self.save_plotly_figure(self.extracted_signal_fig, "Extracted Pulse Signal", width=plot_width, height=plot_height)

        # Particle Velocity
        self.particle_velocity_fig = self.create_base_figure("Particle Velocity", "Time (ms)",
                                                             "Velocity (m/s)", "Velocity Series", font_size = f_size)
        for exp_id, exp in enumerate(self.experiments):
            if self.experiments_test_type[exp_id].split('#')[-1] == "SpecimenTest":
                specimen_metadata = exp.get_instances_of_class("dynamat:SHPBSpecimen")[0]
                specimen_material = exp.get_objects(specimen_metadata, "dynamat:hasMaterial")[0]
                material_name = exp.get_objects(specimen_material, "dynamat:hasLegendName")[0]
            else:
                material_name = "Pulse Test"
            x_data = self.get_series_data(exp, "dynamat:TimeExtractedSignal")
            y_data = self.get_series_data(exp, "dynamat:ParticleVelocity")
            self.add_fig_data(self.particle_velocity_fig, x_data, y_data, line_width, material_name, reverse_y = True) 
        self.save_plotly_figure(self.particle_velocity_fig, "Particle Velocity", width=plot_width, height=plot_height)

        # Strain Rate
        self.strain_rate_fig = self.create_base_figure("Average Strain Rate", "Time (ms)",
                                                       "Strain Rate (1/s)", "Strain Rate", font_size = f_size)
        for exp_id, exp in enumerate(self.experiments):
            if self.experiments_test_type[exp_id].split('#')[-1] == "SpecimenTest":
                specimen_metadata = exp.get_instances_of_class("dynamat:SHPBSpecimen")[0]
                specimen_material = exp.get_objects(specimen_metadata, "dynamat:hasMaterial")[0]
                material_name = exp.get_objects(specimen_material, "dynamat:hasLegendName")[0]
                x_data = self.get_series_data(exp, "dynamat:TimeExtractedSignal")
                y_data = self.get_series_data(exp, "dynamat:EngineeringStrainRate")
                self.add_fig_data(self.strain_rate_fig, x_data, y_data, line_width, material_name, reverse_y = True) 
        self.save_plotly_figure(self.strain_rate_fig, "Average Strain Rate", width=plot_width, height=plot_height)

        # Engineering Strain
        self.eng_strain_rate_fig = self.create_base_figure("Engineering Strain", "Time (ms)",
                                                           "Strain (mm/mm)", "Engineering Strain", font_size=  f_size)
        for exp in self.experiments:
            if self.experiments_test_type[exp_id].split('#')[-1] == "SpecimenTest":
                specimen_metadata = exp.get_instances_of_class("dynamat:SHPBSpecimen")[0]
                specimen_material = exp.get_objects(specimen_metadata, "dynamat:hasMaterial")[0]
                material_name = exp.get_objects(specimen_material, "dynamat:hasLegendName")[0]
                x_data = self.get_series_data(exp, "dynamat:TimeExtractedSignal")
                y_data = self.get_series_data(exp, "dynamat:EngineeringStrain")
                self.add_fig_data(self.eng_strain_rate_fig, x_data, y_data, line_width, material_name, reverse_y = True) 
        self.save_plotly_figure(self.eng_strain_rate_fig, "Engineering Strain", width=plot_width, height=plot_height)

        # True Strain
        self.true_strain_fig = self.create_base_figure("True Strain", "Time (ms)",
                                                       "Strain (mm/mm)", "True Strain", font_size = f_size)
        for exp in self.experiments:
            if self.experiments_test_type[exp_id].split('#')[-1] == "SpecimenTest":
                specimen_metadata = exp.get_instances_of_class("dynamat:SHPBSpecimen")[0]
                specimen_material = exp.get_objects(specimen_metadata, "dynamat:hasMaterial")[0]
                material_name = exp.get_objects(specimen_material, "dynamat:hasLegendName")[0]
                x_data = self.get_series_data(exp, "dynamat:TimeExtractedSignal")
                y_data = self.get_series_data(exp, "dynamat:TrueStrain")
                self.add_fig_data(self.true_strain_fig, x_data, y_data, line_width, material_name, reverse_y = True) 
        self.save_plotly_figure( self.true_strain_fig, "True Strain", width=plot_width, height=plot_height)

        # Engineering Stress
        self.eng_stress_fig = self.create_base_figure("Engineering Stress", "Time (ms)",
                                                      "Stress (MPa)", "Engineering Stress", font_size = f_size)
        for exp in self.experiments:
            if self.experiments_test_type[exp_id].split('#')[-1] == "SpecimenTest":
                specimen_metadata = exp.get_instances_of_class("dynamat:SHPBSpecimen")[0]
                specimen_material = exp.get_objects(specimen_metadata, "dynamat:hasMaterial")[0]
                material_name = exp.get_objects(specimen_material, "dynamat:hasLegendName")[0]
                x_data = self.get_series_data(exp, "dynamat:TimeExtractedSignal")
                y_data = self.get_series_data(exp, "dynamat:EngineeringStress")
                self.add_fig_data(self.eng_stress_fig, x_data, y_data, line_width, material_name, reverse_y = True) 
        self.save_plotly_figure(self.eng_stress_fig, "Engineering Stress", width=plot_width, height=plot_height)

        # True Stress
        self.true_stress_fig = self.create_base_figure("True Stress", "Time (ms)",
                                                       "Stress (MPa)", "True Stress", font_size = f_size)
        for exp in self.experiments:
            if self.experiments_test_type[exp_id].split('#')[-1] == "SpecimenTest":
                specimen_metadata = exp.get_instances_of_class("dynamat:SHPBSpecimen")[0]
                specimen_material = exp.get_objects(specimen_metadata, "dynamat:hasMaterial")[0]
                material_name = exp.get_objects(specimen_material, "dynamat:hasLegendName")[0]
                x_data = self.get_series_data(exp, "dynamat:TimeExtractedSignal")
                y_data = self.get_series_data(exp, "dynamat:TrueStress")
                self.add_fig_data(self.true_stress_fig , x_data, y_data, line_width, material_name, reverse_y = True) 
        self.save_plotly_figure(self.true_stress_fig, "True Stress", width=plot_width, height=plot_height)

        # Engineering Stress - Strain
        self.eng_stress_strain_fig = self.create_base_figure("Engineering Stress - Strain",
                                                             "Strain (mm/mm)", "Stress (MPa)", "Engineering Stress",
                                                             font_size = f_size)
        for exp in self.experiments:
            if self.experiments_test_type[exp_id].split('#')[-1] == "SpecimenTest":
                specimen_metadata = exp.get_instances_of_class("dynamat:SHPBSpecimen")[0]
                specimen_material = exp.get_objects(specimen_metadata, "dynamat:hasMaterial")[0]
                material_name = exp.get_objects(specimen_material, "dynamat:hasLegendName")[0]
                x_data = self.get_series_data(exp, "dynamat:EngineeringStrain")
                y_data = self.get_series_data(exp, "dynamat:EngineeringStress")
                self.add_fig_data(self.eng_stress_strain_fig , x_data, y_data, line_width, material_name, reverse_x = True, reverse_y = True) 
        self.save_plotly_figure(self.eng_stress_strain_fig, "Engineering Stress - Strain", width=plot_width, height=plot_height)

        # True Stress - Strain
        self.true_stress_strain_fig = self.create_base_figure("True Stress - Strain", "Strain (mm/mm)",
                                                              "Stress (MPa)", "True Stress",
                                                              font_size = f_size)
        for exp in self.experiments:
            if self.experiments_test_type[exp_id].split('#')[-1] == "SpecimenTest":
                specimen_metadata = exp.get_instances_of_class("dynamat:SHPBSpecimen")[0]
                specimen_material = exp.get_objects(specimen_metadata, "dynamat:hasMaterial")[0]
                material_name = exp.get_objects(specimen_material, "dynamat:hasLegendName")[0]                
                x_data = self.get_series_data(exp, "dynamat:TrueStrain")
                y_data = self.get_series_data(exp, "dynamat:TrueStress")
                self.add_fig_data(self.true_stress_strain_fig, x_data, y_data, line_width, material_name, reverse_x = True, reverse_y = True) 
        self.save_plotly_figure(self.true_stress_strain_fig, "True Stress Strain", width=plot_width, height=plot_height)

        # Strain Energies
        self.strain_energies_fig = self.create_base_figure("Strain Energies", "Time (ms)",
                                                           "Strain Energy (mJ)", "Strain Energy", font_size = f_size)
        for exp in self.experiments:
            if self.experiments_test_type[exp_id].split('#')[-1] == "SpecimenTest":
                specimen_metadata = exp.get_instances_of_class("dynamat:SHPBSpecimen")[0]
                specimen_material = exp.get_objects(specimen_metadata, "dynamat:hasMaterial")[0]
                material_name = exp.get_objects(specimen_material, "dynamat:hasLegendName")[0]
                x_data = self.get_series_data(exp, "dynamat:TimeExtractedSignal")
                y_data = self.get_series_data(exp, "dynamat:StrainEnergy")
                self.add_fig_data(self.strain_energies_fig , x_data, y_data, line_width, material_name) 
        self.save_plotly_figure(self.strain_energies_fig, "Strain Energies", width=plot_width, height=plot_height)

        # Absorbed Energies
        self.absorbed_energies_fig = self.create_base_figure("Absorbed Energies", "Time (ms)",
                                                             "Energy (mJ)", "Energy Series", font_size= f_size)
        for exp in self.experiments:
            if self.experiments_test_type[exp_id].split('#')[-1] == "SpecimenTest":
                specimen_metadata = exp.get_instances_of_class("dynamat:SHPBSpecimen")[0]
                specimen_material = exp.get_objects(specimen_metadata, "dynamat:hasMaterial")[0]
                material_name = exp.get_objects(specimen_material, "dynamat:hasLegendName")[0]
                x_data = self.get_series_data(exp, "dynamat:TimeExtractedSignal")
                y_data = self.get_series_data(exp, "dynamat:AbsorbedEnergy")
                self.add_fig_data(self.absorbed_energies_fig , x_data, y_data, line_width, material_name)
        self.save_plotly_figure(self.absorbed_energies_fig, "Absorbed Energies", width=plot_width, height=plot_height)       
        
    
    def add_fig_data(self, fig, x_data, y_data, line_width, group_name,  reverse_x = False, reverse_y = False):
        """
        Add data to a Plotly figure with a dynamically extended color scheme.
    
        Args:
            fig (go.Figure): The Plotly figure object.
            x_data (array-like): The X-axis data.
            y_data (DataFrame): The Y-axis data with one or more columns.
    
        Returns:
            None
        """
        # Define mrybm color scale
        mrybm_colors = [
            "rgb(0, 0, 255)",   # Blue
            "rgb(255, 0, 0)",   # Red
            "rgb(0, 128, 0)",   # Green
            "rgb(255, 165, 0)", # Orange                                   
            "rgb(75, 0, 130)",  # Indigo
            "rgb(238, 130, 238)"# Violet
        ]

        factor_x = -1 if reverse_x else 1
        factor_y = -1 if reverse_y else 1
    
        # Get the current number of traces in the figure
        current_trace_count = len(fig.data)
        if len(self.experiments) == 1:
            for idx in range(y_data.shape[1]):
                # Calculate the color index dynamically to avoid repeating colors
                color = mrybm_colors[(current_trace_count + idx) % len(mrybm_colors)]
        
                fig.add_trace(
                    go.Scatter(
                        x=np.copy(x_data.iloc[:,0]) * factor_x,
                        y=np.copy(y_data.iloc[:, idx]) * factor_y,
                        mode="lines",
                        name=f"{y_data.columns[idx]}",
                        line=dict(color=color, width=line_width),
                    )
                )
        else:
            for idx in range(y_data.shape[1]):
                # Calculate the color index dynamically to avoid repeating colors
                color = mrybm_colors[(current_trace_count + idx) % len(mrybm_colors)]
        
                fig.add_trace(
                    go.Scatter(
                        x=np.copy(x_data.iloc[:,0]) * factor_x,
                        y=np.copy(y_data.iloc[:, idx]) * factor_y,
                        mode="lines",
                        name=f"{group_name} {y_data.columns[idx]}",
                        line=dict(color=color, width=line_width),
                    )
                )
        return
            
    def create_base_figure(self, fig_title, x_label, y_label, legend_title, width=1200, height=600, font_size = 20):
        """
        Create a Plotly figure based on the given data and settings.

        Args:
            x_data (array-like): The data for the x-axis (e.g., time or strain values).
            y_data (DataFrame): The data for the y-axis with one or more columns.
                               Each column represents a different series.
            figure_name (str): Name for the figure to use when saving it later.
            fig_title (str): Title of the figure.
            x_label (str): Label for the x-axis.
            y_label (str): Label for the y-axis.
            legend_title (str): Title for the legend.

        Returns:
            go.Figure: A Plotly figure object.
        """
        # Initialize the figure
        fig = go.Figure()
        
        # Update layout with titles, labels, and style
        fig.update_layout(
            width=width,
            height=height,  # Figure size
            plot_bgcolor="#F5F5F5",  # Background of the plot area
            paper_bgcolor="#FFFFFF",  # Background of the entire figure
            title=dict(
                text=fig_title,
                x=0.5,
                y=0.95,
                xanchor="center",
                font=dict(size=font_size+4, color="black", family="Arial"),
            ),
            xaxis=dict(
                title=x_label,
                titlefont=dict(size=font_size, color="black", family="Arial"),
                tickfont=dict(size=font_size, color="black", family="Arial"),
                showgrid=True,
                gridcolor="lightgrey",
                gridwidth=1,
            ),
            yaxis=dict(
                title=y_label,
                titlefont=dict(size=font_size, color="black", family="Arial"),
                tickfont=dict(size=font_size, color="black", family="Arial"),
                showgrid=True,
                gridwidth=1,
                gridcolor="lightgrey",
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor="grey",
            ),
            legend=dict(
                title=legend_title,
                x = 0.5, 
                y = 1.0 ,
                xanchor="center",
                yanchor="bottom",
                orientation="h",
                font=dict(size=font_size-6, color="black", family="Arial"),
                bgcolor="#FFFFFF",
                bordercolor="black",
                borderwidth=2,
            ),
        )

        return fig

    def get_series_data(self, experiment, series_class_uri):
        """
        Retrieves all instances for a given class as a pandas DataFrame.

        Args:
            series_class_uri (str): The class of gauge sensors to fetch signals for.

        Returns:
            pd.DataFrame: A DataFrame where each column represents a signal with the column name as the gauge sensor name.
        """
        signals_df = pd.DataFrame()

        sensor_data_instances = experiment.get_instances_of_class(series_class_uri)

        for sensor_name in sensor_data_instances:
            # Fetch relevant properties for the sensor
            signal_data = experiment.get_objects(sensor_name, "dynamat:hasEncodedData")[0]
            signal_encoding = experiment.get_objects(sensor_name, "dynamat:hasEncoding")[0]
            signal_size = int(experiment.get_objects(sensor_name, "dynamat:hasSize")[0])
            signal_legend = experiment.get_objects(sensor_name, "dynamat:hasLegendName")[0]

            # Decode and validate the data
            try:
                if signal_encoding == "base64Binary":
                    decoded_data = base64.b64decode(signal_data)
                    signal_array = np.frombuffer(decoded_data, dtype=np.float32)

                    if len(signal_array) == signal_size:
                        signals_df[signal_legend] = signal_array
            except Exception as e:
                print(f"Error processing {sensor_name}: {e}")

        return signals_df

    def save_plotly_figure(self, figure, figure_name, width, height):
        """
        Save a Plotly figure to a temporary HTML file with specified size.
    
        Args:
            figure (go.Figure): The Plotly figure object to save.
            figure_name (str): The name of the figure (for the selection box and reference).
            width (int): The width of the figure in pixels.
            height (int): The height of the figure in pixels.
        """
        try:
            # Update figure size dynamically
            figure.update_layout(width=width, height=height)
    
            # Save the figure as an HTML file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8")
            figure.write_html(temp_file.name)
            self.temp_files[figure_name] = temp_file.name
            self.figure_objects[figure_name] = figure  
        except Exception as e:
            print(f"Error saving figure: {e}")


    def display_selected_figure(self):
        """
        Display the selected figure in the QWebEngineView.
        """
        selected_figure_name = self.selection_box.currentText()
        if selected_figure_name in self.temp_files:
            figure_path = self.temp_files[selected_figure_name]
            self.figure_view.setUrl(QUrl.fromLocalFile(figure_path))
    
    def update_layout(self):
        """
        Update the layout dynamically based on the selected view mode and resize plots.
        """
        # Clear the current layout
        # Clear the current layout
        for i in reversed(range(self.figure_layout.count())):
            widget = self.figure_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                
        # Get the selected view mode
        view_mode = self.view_mode_combo.currentText()
        rows, cols = (1, 1) if view_mode == "Single" else (2, 1) if view_mode == "Dual" else (2, 2)
        line_width = 3 if view_mode == "Single" else 2 if view_mode == "Dual" else 1
        font_size = 20 if view_mode == "Single" else 18 if view_mode == "Dual" else 14
        
        # Calculate dynamic plot size
        container_width = self.width() - 50  # Subtract padding/margin
        container_height = self.height() - 150  # Subtract padding for controls
        plot_width = container_width // cols
        plot_height = container_height // rows

        self.populate_figures(plot_width, plot_height, line_width, font_size) 
    
        # Update figure layout sizes dynamically
        for idx in range(rows * cols):
            if idx >= len(self.plot_widgets):
                self.create_plot_widget(idx)  # Create new widgets if needed
            selection_box, web_view, container = self.plot_widgets[idx]
            row, col = divmod(idx, cols)
            self.figure_layout.addWidget(container, row, col)
    
            # Dynamically resize the figure for the web view
            if selection_box.currentText() in self.temp_files:
                figure_path = self.temp_files[selection_box.currentText()]
                web_view.setUrl(QUrl.fromLocalFile(os.path.abspath(figure_path)))


    def create_plot_widget(self, index):
        """
        Create a new widget with a selection box and figure display.
        """
        # Container widget for selection box, button, and web view
        container = QWidget()
        layout = QVBoxLayout()
        container.setLayout(layout)

        # Create a horizontal layout for the selection box and button
        control_layout = QHBoxLayout()
    
        # Create the selection box
        selection_box = QComboBox()
        selection_box.addItems(self.temp_files.keys())  # Add available figures
        selection_box.currentTextChanged.connect(lambda fig_name, idx=index: self.update_figure(idx, fig_name))
        control_layout.addWidget(selection_box)

        # Save button
        save_button = QPushButton("Save as CSV")
        save_button.clicked.connect(lambda idx=index: self.save_current_plot_data(idx))
        control_layout.addWidget(save_button)

        # Save as Image Button
        save_image_button = QPushButton("Save as Image")
        save_image_button.clicked.connect(lambda idx=index: self.save_current_plot_image(idx))
        control_layout.addWidget(save_image_button)

        # Add the control layout to the main layout
        layout.addLayout(control_layout)
    
        # Create the web view for figure display
        web_view = QWebEngineView()
        web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        layout.addWidget(web_view)
    
        # Store the widget and its components
        self.plot_widgets.append((selection_box, web_view, container))

    def add_plot_widget(self, idx, rows, cols):
        """
        Add the plot widget to the grid layout.
        """
        selection_box, web_view = self.plot_widgets[idx]
        row, col = divmod(idx, cols)
        self.figure_layout.addWidget(selection_box.parentWidget(), row, col)

    def update_figure(self, index, figure_name):
        """
        Update the figure in the specified plot widget.
        """
        selection_box, web_view, _ = self.plot_widgets[index]
        if figure_name in self.temp_files:
            figure_path = self.temp_files[figure_name]
            web_view.setUrl(QUrl.fromLocalFile(os.path.abspath(figure_path)))

    def save_current_plot_data(self, index):
        """
        Save the current plot data to a CSV file, formatted with X values as one column and Y values in separate columns.
        """
        # Get the selected figure name
        selection_box, web_view, _ = self.plot_widgets[index]
        selected_figure_name = selection_box.currentText()
    
        # Check if the figure exists
        if selected_figure_name not in self.temp_files:
            print("No figure data available to save.")
            return
    
        # Extract the figure data from the temp files directly
        figure = self.figure_objects[selected_figure_name]
    
        if not figure:
            print("Failed to load the figure for saving.")
            return
    
        # Initialize a DataFrame to store formatted data
        formatted_data = pd.DataFrame()
        
        x_axis_title = figure.layout.xaxis.title.text if figure.layout.xaxis.title.text else "X"
        
        # Loop through traces and format data
        for trace in figure.data:
            if hasattr(trace, "x") and hasattr(trace, "y") and trace.x is not None and trace.y is not None:
                x_series = pd.Series(trace.x, name=x_axis_title)
                y_series = pd.Series(trace.y, name=trace.name)
                if formatted_data.empty:
                    formatted_data = pd.concat([x_series, y_series], axis=1)
                else:
                    formatted_data = formatted_data.join(y_series, how="outer")
    
        # Prompt the user to save the CSV file
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(self, "Save Plot Data", "", "CSV Files (*.csv)")
    
        if file_path:
            try:
                # Save the formatted data to CSV
                formatted_data.to_csv(file_path, index=False)
                print(f"Plot data saved to {file_path}")
            except Exception as e:
                print(f"Error saving CSV: {e}")
                
    def save_current_plot_image(self, index):
            """
            Save the current plot as an image.
            """
            selection_box, web_view, _ = self.plot_widgets[index]
            selected_figure_name = selection_box.currentText()
    
            # Prompt user to select a file path
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getSaveFileName(self, "Save Plot Image", "", "PNG Files (*.png);;JPEG Files (*.jpg);;SVG Files (*.svg)")
            if file_path:
                try:
                    # Save the current figure as an image
                    self.figure_objects[selected_figure_name].write_image(file_path)
                    print(f"Plot saved to {file_path}")
                except Exception as e:
                    print(f"Error saving image: {e}")

                
    def closeEvent(self, event):
        """
        Handle cleanup when the window is closed.
        """
        for temp_file in self.temp_files.keys():
            try:
                os.remove(self.temp_files[temp_file])
            except Exception as e:
                print(f"Error deleting temporary file {temp_file}: {e}")
        super().closeEvent(event)
