import createPlotlyComponent from 'react-plotly.js/factory';

// plotly.js-basic-dist-min exposes a UMD bundle; use require to avoid type friction.
// eslint-disable-next-line @typescript-eslint/no-var-requires
const Plotly: any = require('plotly.js-basic-dist-min');

const Plot = createPlotlyComponent(Plotly);

export default Plot;
