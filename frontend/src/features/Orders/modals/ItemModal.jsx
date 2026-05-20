import PropTypes from "prop-types";
import Modal from "./Modal";
import MultiLineCalculator from "../../cost-calculator/MultiLineCalculator";
import CostCalculatorPage from "../../cost-calculator/CostCalculatorPage";

const ItemModal = ({ item, onClose, hideActionButtons=true}) => (
  <Modal onClose={onClose} size="large">
    { item.printings.length === 1 && item.operations.length === 0 && (
    <CostCalculatorPage
      edition={item.printings[0].edition} 
      production={item.printings[0].production}
      economy={item.economy}
      hideActionButtons={hideActionButtons}
    />
    )}
    { (item.printings.length !== 1 || item.operations.length > 0)  && (
    <MultiLineCalculator
      initial_data={item}
      hideActionButtons={hideActionButtons}
    />
    )}
  </Modal>
);

ItemModal.propTypes = {
  item: PropTypes.object.isRequired,
  onClose: PropTypes.func.isRequired,
};

export default ItemModal;
