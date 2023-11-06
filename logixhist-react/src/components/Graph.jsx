import { Line } from 'react-chartjs-2';
// import { useEffect, useState } from "react";

// import '../assets/styles/list-groups.css'
// import '../assets/styles/bootstrap.min.css';

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

// const chartData = {
//   labels: ["test"],
//   datasets: [
//     {
//       label: "Prices",
//       data: [1,3,4],
//       borderColor: "black",
//     },
//   ]
// }

const chartData = {
  labels: ["January", "February", "March", "April", "May"],
  datasets: [
    {
      label: "Temperature",
      data: [10, 20, 15, 30, 25],
      borderColor: "red",
      fill: true,
    },
    {
      label: "Power",
      data: ['ON', 'ON', 'OFF', 'ON', 'OFF'],
      borderColor: "blue",
      fill: true,
      yAxisID: 'power',
      stepped: true
    },
  ],
};

const options = {
  scales: {
    y: {
      beginAtZero: true,
      stack: 'power'
    },
    power:{
      type: "category",
      labels: ["ON", "OFF"],
      stack: "power",
      offset: true
    }
  },
};


function Graph() {
  return (
    <div>
      <h2>Trending Data</h2>
      <Line data={chartData} options={options} />
    </div>
  );
}

export default Graph;