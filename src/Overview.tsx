import { ArrowRight } from 'lucide-react';
import image1 from './1.jpeg';
import image2 from './2.jpeg';
import image3 from './3.jpeg';

const Overview = () => {
  // JSON data for each image
  const data1 = [
    {
        "Parameter": "aXo",
        "All Farms": "(n 34) 4.582"
    },
    {
        "Parameter": "",
        "All Farms": "(0.548)"
    },
    {
        "Parameter": "S ,\"",
        "All Farms": "-0.567 ~~~~~(0 .253)"
    },
    {
        "Parameter": "81",
        "All Farms": "~~~~~~1. 614* (0. 549)"
    },
    {
        "Parameter": "32 ,,*",
        "All Farms": "- 1. 359* (1.274)"
    },
    {
        "Parameter": "63",
        "All Farms": "-0. 588* (0.485)"
    },
    {
        "Parameter": "6,,",
        "All Farms": "0.296"
    },
    {
        "Parameter": "",
        "All Farms": "(0.715)"
    },
    {
        "Parameter": "aj *",
        "All Farms": "- 2.141** (1.200)"
    },
    {
        "Parameter": "02",
        "All Farms": "-0.588 (0.274) 1.797"
    },
    {
        "Parameter": "X2",
        "All Farms": "(0.233) 0.185 0.896"
    }
  ];

  const data2 = [
    {
        "": "",
        "Large": "Farms",
        "Small": "Farms"
    },
    {
        "": "Geometric Means",
        "Large": "",
        "Small": ""
    },
    {
        "": "II (rupees)",
        "Large": "2,184.62",
        "Small": "493.90"
    },
    {
        "": "K (rupees)",
        "Large": "51.35",
        "Small": "22.89"
    },
    {
        "": "T (acres)",
        "Large": "23.81",
        "Small": "3.99"
    },
    {
        "": "Rates of Return R!! (rupees per rupee) .9K",
        "Large": "-25.02",
        "Small": "-12.69"
    },
    {
        "": "AT (rupees per acre)",
        "Large": "164.88",
        "Small": "222.44"
    }
  ];

  const data3 = [
    {
        "State": "West Bengal",
        "T": "12.15",
        "K": "127.33",
        "L": "402.41",
        "wII": "1.54",
        "": "923.28",
        "V": "1,811.56"
    },
    {
        "State": "West Bengal",
        "T": "16.96",
        "K": "116.00",
        "L": "628.37",
        "wII": "1.61",
        "": "772.36",
        "V": "2,403.23"
    },
    {
        "State": "West Bengal",
        "T": ".64",
        "K": "7.44",
        "L": "39.05",
        "wII": "1.60",
        "": "187.78",
        "V": "129.41"
    },
    {
        "State": "West Bengal",
        "T": "1.81",
        "K": "14.84",
        "L": "97.96",
        "wII": "1.49",
        "": "373.03",
        "V": "352.59"
    },
    {
        "State": "West Bengal",
        "T": "3.11",
        "K": "25.19",
        "L": "173.10",
        "wII": "1.59",
        "": "555.87",
        "V": "547.05"
    },
    {
        "State": "West Bengal",
        "T": "4.47",
        "K": "33.30",
        "L": "213.58",
        "wII": "1.53",
        "": "1,948.21",
        "V": "809.07"
    },
    {
        "State": "West Bengal",
        "T": "6.18",
        "K": "41.59",
        "L": "321.42",
        "wII": "1.45",
        "": "813.20",
        "V": "1,158.13"
    },
    {
        "State": "West Bengal",
        "T": "8.15",
        "K": "37.89",
        "L": "323.80",
        "wII": "1.54",
        "": "955.08",
        "V": "1,401.80"
    },
    {
        "State": "Madras",
        "T": "11.81",
        "K": "86.21",
        "L": "336.58",
        "wII": ".54",
        "": "1,653.61",
        "V": "907.01"
    },
    {
        "State": "Madras",
        "T": "17.35",
        "K": "93.69",
        "L": "395.58",
        "wII": ".56",
        "": "2,215.54",
        "V": "1,174.59"
    },
    {
        "State": "Madras",
        "T": "22.97",
        "K": "103.36",
        "L": "560.41",
        "wII": ".62",
        "": "2,248.45",
        "V": "1,683.70"
    },
    {
        "State": "Madras",
        "T": "43.78",
        "K": "205.76",
        "L": "897.49",
        "wII": ".55",
        "": "5,838.73",
        "V": "3,607.47"
    },
    {
        "State": "Madras",
        "T": "1.61",
        "K": "39.60",
        "L": "179.35",
        "wII": ".62",
        "": "426.00",
        "V": "354.04"
    },
    {
        "State": "Madras",
        "T": "3.66",
        "K": "37.69",
        "L": "229.85",
        "wII": ".52",
        "": "716.90",
        "V": "751.03"
    },
    {
        "State": "Madras",
        "T": "6.02",
        "K": "67.42",
        "L": "276.92",
        "wII": ".56",
        "": "2,045.88",
        "V": "947.55"
    },
    {
        "State": "Madras",
        "T": "8.83",
        "K": "98.89",
        "L": "342.60",
        "wII": ".56",
        "": "763.14",
        "V": "1,190.28"
    },
    {
        "State": "Madhya Pradesh",
        "T": "12.44",
        "K": "9.57",
        "L": "294.70",
        "wII": "1.08",
        "": "1,709.28",
        "V": "1,479.12"
    },
    {
        "State": "Madhya Pradesh",
        "T": "17.19",
        "K": "11.86",
        "L": "403.45",
        "wII": "1.00",
        "": "6,718.47",
        "V": "1,693.21"
    },
    {
        "State": "Madhya Pradesh",
        "T": "24.25",
        "K": "14.55",
        "L": "470.21",
        "wII": "1.11",
        "": "40.53",
        "V": "2,616.57"
    },
    {
        "State": "Madhya Pradesh",
        "T": "34.77",
        "K": "31.64",
        "L": "756.25",
        "wII": "1.04",
        "": "144.37",
        "V": "3,689.10"
    },
    {
        "State": "Madhya Pradesh",
        "T": "45.17",
        "K": "41.10",
        "L": "1,084.08",
        "wII": "1.11",
        "": "157.86",
        "V": "4,458.28"
    },
    {
        "State": "Madhya Pradesh",
        "T": "93.36",
        "K": "82.15",
        "L": "1,831.72",
        "wII": "1.15",
        "": "334.62",
        "V": "10,017.53"
    },
    {
        "State": "Madhya Pradesh",
        "T": "2.95",
        "K": "3.42",
        "L": "101.13",
        "wII": ".94",
        "": "513.87",
        "V": "422.73"
    },
    {
        "State": "Madhya Pradesh",
        "T": "7.38",
        "K": "8.63",
        "L": "190.40",
        "wII": "1.06",
        "": "729.34",
        "V": "849.44"
    },
    {
        "State": "Uttar Pradesh",
        "T": "12.00",
        "K": "78.00",
        "L": "602.40",
        "wII": "1.06",
        "": "7.57",
        "V": "2,448.00"
    },
    {
        "State": "Uttar Pradesh",
        "T": "16.90",
        "K": "95.99",
        "L": "765.57",
        "wII": "1.06",
        "": "320.98",
        "V": "3,380.00"
    },
    {
        "State": "Uttar Pradesh",
        "T": "27.58",
        "K": "148.93",
        "L": "1,073.14",
        "wII": "1.01",
        "": "384.68",
        "V": "5,653.90"
    },
    {
        "State": "Uttar Pradesh",
        "T": "3.33",
        "K": "31.00",
        "L": "209.16",
        "wII": "1.01",
        "": "411.48",
        "V": "922.41"
    },
    {
        "State": "Uttar Pradesh",
        "T": "7.68",
        "K": "64.97",
        "L": "432.84",
        "wII": ".98",
        "": "227.80",
        "V": "1,843.20"
    },
    {
        "State": "Punjab",
        "T": "14.50",
        "K": "19.57",
        "L": "450.22",
        "wII": "1.51",
        "": "448.19",
        "V": "2,463.55"
    },
    {
        "State": "Punjab",
        "T": "28.45",
        "K": "20.48",
        "L": "701.86",
        "wII": "1.38",
        "": "124.41",
        "V": "4,056.97"
    },
    {
        "State": "Punjab",
        "T": "81.19",
        "K": "30.85",
        "L": "1,484.96",
        "wII": "1.92",
        "": "391.14",
        "V": "12,957.92"
    },
    {
        "State": "Punjab",
        "T": "3.98",
        "K": "8.95",
        "L": "158.96",
        "wII": "1.33",
        "": "129.43",
        "V": "702.47"
    }
  ];

  const renderTable = (data: any[], title: string) => {
    if (data.length === 0) return null;
    
    return (
      <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
        <h3 className="text-xl font-semibold text-white mb-4">{title}</h3>
        <div className="bg-gray-900 rounded-lg p-3 overflow-x-auto max-h-96 overflow-y-auto">
          <pre className="text-xs text-green-400 whitespace-pre-wrap">
            <code>{JSON.stringify(data, null, 2)}</code>
          </pre>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <div className="container mx-auto px-6 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4 text-white">
            Data Extraction Overview
          </h1>
          <p className="text-white/80 text-lg">
            Examples of PDF table extraction results from Octro
          </p>
        </div>

        {/* Data Showcase */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
          
          {/* Example 1 */}
          <div className="space-y-6">
            <div className="text-center">
              <img 
                src={image1} 
                alt="PDF Table Example 1" 
                className="w-full max-w-md mx-auto rounded-lg shadow-lg"
              />
              <p className="text-white/60 mt-2">Original PDF Table</p>
            </div>
            {renderTable(data1, "Extracted Data - Statistical Analysis")}
          </div>

          {/* Example 2 */}
          <div className="space-y-6">
            <div className="text-center">
              <img 
                src={image2} 
                alt="PDF Table Example 2" 
                className="w-full max-w-md mx-auto rounded-lg shadow-lg"
              />
              <p className="text-white/60 mt-2">Original PDF Table</p>
            </div>
            {renderTable(data2, "Extracted Data - Farm Comparison")}
          </div>

        </div>

        {/* Example 3 - Full Width */}
        <div className="mt-12 space-y-6">
          <div className="text-center">
            <img 
              src={image3} 
              alt="PDF Table Example 3" 
              className="w-full max-w-2xl mx-auto rounded-lg shadow-lg"
            />
            <p className="text-white/60 mt-2">Original PDF Table</p>
          </div>
          {renderTable(data3, "Extracted Data - Regional Statistics")}
        </div>

        {/* CTA Section */}
        <div className="text-center mt-16">
          <h2 className="text-2xl font-bold mb-4">
            Extract Your Own PDF Tables
          </h2>
          <p className="text-white/80 mb-8 max-w-2xl mx-auto">
            Transform your PDF documents into structured data with our advanced extraction technology. 
            Support for complex tables, multiple formats, and high accuracy.
          </p>
          <a 
            href="/pricing" 
            className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3 rounded-lg font-medium transition-all transform hover:scale-105"
          >
            Try Octro Now
            <ArrowRight className="w-5 h-5" />
          </a>
        </div>
      </div>
    </div>
  );
};

export default Overview;