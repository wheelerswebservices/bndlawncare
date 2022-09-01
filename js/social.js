import React from 'react';

class SocialComp extends React.Component {
	render(){
		let data = this.props.data;
		return (
			<div className="social-wrap">
			{
				data.icons.map((record, idx) => {
					return (
						<SocialRecordComp
							key={idx}
							href={record.href}
							icon={record.icon}
							title={record.title}
						/>
					)
				})
			}
			</div>
		)
	}
}

class SocialRecordComp extends React.Component {
	render(){
		let target = this.props.href.startsWith("#") ? "_self" : "_blank";
		return (
			<a className="social-data" title={this.props.title} target={target} href={this.props.href}>
				<i className={"accent fa fa-" + this.props.icon}></i>
			</a>
		)
	}
}

export default SocialComp;
export { SocialRecordComp };
