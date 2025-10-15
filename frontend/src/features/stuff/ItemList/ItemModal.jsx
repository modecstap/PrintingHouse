import PropTypes from "prop-types";
import Modal from "../Modal/Modal";
import CostCalculatorPage from "../../cost-calculator/CostCalculatorPage";

const ItemModal = ({ item, onClose, hideActionButtons=true}) => (
  <Modal onClose={onClose} size="large">
    <CostCalculatorPage
      edition={item.edition || {}}
      production={item.production || {}}
      hideActionButtons={hideActionButtons}
    />
  </Modal>
);

ItemModal.propTypes = {
  item: PropTypes.object.isRequired,
  onClose: PropTypes.func.isRequired,
};

export default ItemModal;
