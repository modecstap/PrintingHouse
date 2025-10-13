import PropTypes from "prop-types";
import Modal from "../Modal/Modal";
import CostCalculatorPage from "../../cost-calculator/CostCalculatorPage";

const ItemModal = ({ item, onClose }) => (
  <Modal onClose={onClose} size="large">
    <CostCalculatorPage
      edition={item.edition || {}}
      production={item.production || {}}
    />
  </Modal>
);

ItemModal.propTypes = {
  item: PropTypes.object.isRequired,
  onClose: PropTypes.func.isRequired,
};

export default ItemModal;
