// Checkbox: React-friendly checkbox component
//
// Borrowed from https://react.tips/checkboxes-in-react-16


import React from "react";

class Checkbox extends React.Component {
    render() {
        const key = 'checkbox-' + this.props.internalName;
        return (
            <div className="form-check" key={key}>
                <label>
                    <input
                        type="checkbox"
                        name={this.props.internalName}
                        checked={this.props.isSelected}
                        onChange={this.props.onCheckboxChange}
                        className="form-check-input"
                    />
                    {this.props.label}
                </label>
            </div>
            );
    }
}

export { Checkbox };

