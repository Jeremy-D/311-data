import React from 'react';
import PropTypes from 'proptypes';
import { connect } from 'react-redux';
import moment from 'moment';
import { REQUEST_TYPES } from '@components/common/CONSTANTS';
import Chart from './Chart';

const TotalRequests = ({
  frequency: { bins, counts },
}) => {
  if (!bins || !counts) return null;

  // // DATA ////

  const chartData = {
    labels: bins.slice(0, -1).map(bin => moment(bin).format('MMM D')),
    datasets: Object.keys(counts).map(key => {
      const requestType = REQUEST_TYPES[key];
      return {
        data: counts[key],
        label: requestType?.abbrev,
        backgroundColor: requestType?.color,
        barPercentage: 0.9,
        barThickness: 'flex',
      };
    }),
  };

  const exportData = () => {
    const header = bins.slice(0, -1).map(bin => moment(bin).format('MM/DD/YYYY'));
    const rows = chartData.datasets.map(dataset => dataset.data);
    const index = chartData.datasets.map(dataset => dataset.label);

    const totals = header.map((_, idx) => (
      rows.reduce((p, c) => p + c[idx], 0)
    ));

    return {
      header,
      rows: [...rows, totals],
      index: [...index, 'Total'],
    };
  };

  // // OPTIONS ////

  const chartOptions = {
    title: {
      text: 'Total Requests',
    },
    aspectRatio: 11 / 8,
    scales: {
      xAxes: [{
        stacked: true,
        scaleLabel: {
          labelString: 'Timeline',
        },
        gridLines: {
          display: false,
        },
        ticks: {
          minRotation: 45,
          maxRotation: 45,
        },
      }],
      yAxes: [{
        stacked: true,
        scaleLabel: {
          labelString: '# of Requests',
        },
        ticks: {
          beginAtZero: true,
        },
      }],
    },
    tooltips: {
      mode: 'index',
      callbacks: {
        title: tt => {
          const { index } = tt[0];
          const start = moment(bins[index]).format('MMM D');
          const end = moment(bins[index + 1]).subtract(1, 'days').format('MMM D');
          return start === end ? start : `${start} - ${end}`;
        },
        footer: (tooltipItem, data) => {
          const { index } = tooltipItem[0];
          const total = data.datasets.reduce((p, c) => p + c.data[index], 0);
          return `Total ${total}`;
        },
      },
    },
  };

  return (
    <Chart
      id="total-requests"
      type="bar"
      data={chartData}
      options={chartOptions}
      exportData={exportData}
    />
  );
};

const mapStateToProps = state => ({
  frequency: state.data.frequency,
});

export default connect(mapStateToProps)(TotalRequests);

TotalRequests.propTypes = {
  frequency: PropTypes.shape({
    bins: PropTypes.arrayOf(PropTypes.string),
    counts: PropTypes.shape({}),
  }).isRequired,
};
