import React from "react";

export default function ActionModal({ actionType, comment, setComment, onConfirm, onClose, loading }) {
  if (!actionType) return null;

  return (
    <div className="modal-overlay">
      <div className="modal">
        <h3>{actionType === "delay" ? "Отложить заказ" : "Принять в работу"}</h3>
        <textarea
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="Введите комментарий..."
          rows={4}
        />
        <div className="modal-buttons">
          <button className="btn btn-primary" onClick={onConfirm} disabled={loading}>
            {loading ? "Отправляем..." : actionType === "delay" ? "Отложить" : "Принять в работу"}
          </button>
          <button className="btn btn-more" onClick={onClose}>Отмена</button>
        </div>
      </div>
    </div>
  );
}
