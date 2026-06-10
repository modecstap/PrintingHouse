import { useState } from "react";

export default function ImportSection({ setFormData }) {
  const [tzFile, setTzFile] = useState(null);
  const [stockFile, setStockFile] = useState(null);

  const parseCSV = (text) => {
    const [header, ...rows] = text.trim().split("\n");
    const keys = header.split(",");

    return rows.map(row => {
      const values = row.split(",");
      return Object.fromEntries(
        keys.map((k, i) => [k.trim(), values[i].trim()])
      );
    }).map(r => ({
      price: Number(r.price),
      count: Number(r.count),
      width: Number(r.width),
      height: Number(r.height),
      density: Number(r.density),
    }));
  };

  const handleApply = async () => {
    if (!tzFile || !stockFile) {
      alert("Загрузите оба файла");
      return;
    }

    const tzText = await tzFile.text();
    const stockText = await stockFile.text();

    let tzData = JSON.parse(tzText);
    const stockData = parseCSV(stockText);

    // 🔥 Основная логика маппинга
    const newPrintings = tzData.map((item) => {
      // фильтр по плотности
      const matched = stockData
        .filter(s => s.density === item.density)
        .sort((a, b) => b.count - a.count)[0];

      return {
        edition: {
          count: item.count,
          list_size: {
            width: item.width,
            height: item.height,
            bleeds: 2,
          },
          density: item.density,
          chroma: item.printing,
          lamination: item.lamination,
          die_cutting: Boolean(item.die_cuttig),
        },
        production: {
          paper_cost: matched?.price || 0,
          press_sheet: {
            width: matched?.width || 0,
            height: matched?.height || 0,
          },
        },
        comment: "",
      };
    });

    setFormData(prev => ({
      ...prev,
      printings: newPrintings,
    }));
  };

  return (
    <div className="calculator-container">
        <h3>Импорт данных</h3>

        <div className="import-files">
            <div className="import-file">
            <label className="file-input">Тех-задание (JSON):</label>
            <input
                type="file"
                accept=".json"
                onChange={(e) => setTzFile(e.target.files[0])}
            />
            </div>

            <div className="import-file">
            <label className="file-input">Склад (CSV):</label>
            <input
                type="file"
                accept=".csv"
                onChange={(e) => setStockFile(e.target.files[0])}
            />
            </div>
        </div>

        <button className="btn btn-primary" onClick={handleApply}>
            Применить
        </button>
        </div>
  );
}
