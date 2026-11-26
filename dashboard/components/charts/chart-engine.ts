import { init, use } from "echarts/core";
import { BarChart, CustomChart, LineChart, ScatterChart } from "echarts/charts";
import { GridComponent, LegendComponent, MarkLineComponent, TitleComponent, TooltipComponent } from "echarts/components";
import { SVGRenderer } from "echarts/renderers";

use([BarChart, CustomChart, LineChart, ScatterChart, GridComponent, LegendComponent, MarkLineComponent, TitleComponent, TooltipComponent, SVGRenderer]);

export { init };
