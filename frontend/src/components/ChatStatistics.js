import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const ChatStatistics = ({ contactId }) => {
  const [statistics, setStatistics] = useState([]);

  useEffect(() => {
    const fetchStatistics = async () => {
      const response = await fetch(`http://localhost:5000/api/statistics/${contactId}`);
      const data = await response.json();
      setStatistics(data);
    };
    fetchStatistics();
  }, [contactId]);

  const chartData = {
    labels: statistics.map(stat => stat.date),
    datasets: [
      {
        label: 'Message Count',
        data: statistics.map(stat => stat.count),
        fill: false,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
      }
    ]
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Chat Activity Over Time'
      }
    }
  };

  return (
    <div className="chat-statistics">
      <Line data={chartData} options={options} />
    </div>
  );
};

export default ChatStatistics;
