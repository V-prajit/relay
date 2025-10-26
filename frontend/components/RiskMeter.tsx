'use client';

interface RiskMeterProps {
  score: number; // 0-100
}

export default function RiskMeter({ score }: RiskMeterProps) {
  // Determine color based on score
  const getColor = (score: number) => {
    if (score >= 60) return {
      bg: '#fef2f2',
      fill: '#dc2626',
      text: 'High Risk'
    };
    if (score >= 30) return {
      bg: '#fefce8',
      fill: '#ea580c',
      text: 'Medium Risk'
    };
    return {
      bg: '#f0fdf4',
      fill: '#16a34a',
      text: 'Low Risk'
    };
  };

  const color = getColor(score);

  // SVG gauge parameters
  const size = 200;
  const strokeWidth = 20;
  const center = size / 2;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;

  // Calculate arc
  const arcLength = (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <div className="relative" style={{ width: size, height: size }}>
        {/* Background circle */}
        <svg
          width={size}
          height={size}
          className="transform -rotate-90"
        >
          {/* Background track */}
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke="#e5e7eb"
            strokeWidth={strokeWidth}
          />

          {/* Progress arc */}
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke={color.fill}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={circumference - arcLength}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
          />
        </svg>

        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <div className="text-4xl font-bold" style={{ color: color.fill }}>
            {Math.round(score)}
          </div>
          <div className="text-sm text-gray-500">/ 100</div>
        </div>
      </div>

      {/* Risk label */}
      <div
        className="mt-4 px-4 py-2 rounded-full font-medium text-sm"
        style={{ backgroundColor: color.bg, color: color.fill }}
      >
        {color.text}
      </div>
    </div>
  );
}
