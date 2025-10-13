import React, { useState, useEffect } from "react";
import { BackendIP } from "../../../constants/BackendIP"; 
import "./table.css";
import ItemList from "../ItemList/ItemList";

const Table = ({ endPoint, title }) => {
  const [materials, setMaterials] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchMaterials = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`${BackendIP}/${endPoint}`);
      if (response.ok) {
        const data = await response.json();
        setMaterials(data);
      } else {
        throw new Error("Ошибка получения данных.");
      }
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMaterials();
  }, [endPoint]); 

  if (loading) return <div className="loading">Загрузка...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="materials-container">
      <div className="materials-header">
        <h1 className="materials-title">{title}</h1>
        <button className="refresh-button" onClick={fetchMaterials}>&#10226;</button>
      </div>
      <ItemList data={materials} disableAction={false} apiUrl={`${BackendIP}/${endPoint}`} />
    </div>
  );
};

export default Table;
