import { Line } from 'react-chartjs-2';
// import { useEffect, useState } from 'react';

import '../assets/styles/list-groups.css';
// import '../assets/styles/bootstrap.min.css';

import 'chartjs-plugin-annotation';

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  require('chartjs-plugin-annotation')
);

const chartData = {
  labels: ['1', '2', '3', '4', '5'],
  datasets: [
    {
      label: 'Temperature',
      data: [10, 15, 30, 20, 25],
      borderColor: 'red',
      yAxisID: 'Temperature',
    },
    {
      label: 'Power',
      data: [1, 0, 1, 1, 0],
      borderColor: 'blue',
      yAxisID: 'Power',
      stepped: true,
    },
    {
      label: 'Level',
      data: [20, 35, 10, 60, 25],
      borderColor: 'green',
      yAxisID: 'Level'
    },
    {
      label: 'Switch',
      data: [1, 0, 1, 1, 0],
      borderColor: 'orange',
      yAxisID: 'Switch',
      stepped: true,
    },
  ],
};

const options = {
  scales: {
    Temperature:{
      type: 'linear',
      stack: 'trend',
      grid: {
        borderColor: 'red'
      },
    },
    Power:{
      type: 'category',
      labels: ['ON', 'OFF'],
      stack: 'trend',
      grid: {
        borderColor: 'blue'
      },
      offset: true,
    },
    Level:{
      type: 'linear',
      stack: 'trend',
      grid: {
        borderColor: 'red'
      }
    },
    Switch:{
      type: 'category',
      labels: ['ON', 'OFF'],
      stack: 'trend',
      grid: {
        borderColor: 'orange'
      },
      offset: true,
    }
  },
  // annotation: {
  //   annotations: [
  //     {
  //       type: 'line',
  //       mode: 'vertical',
  //       scaleID: 'x',
  //       value: 2,
  //       borderColor: 'orange',
  //       borderWidth: 5,
  //     }
  //   ]
  // }
};


function Graph() {
  return (
    <div>
      <Line data={chartData} options={options} />
    </div>
  );
}

export default Graph;