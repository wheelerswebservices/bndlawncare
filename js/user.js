import React from 'react';

class UserComp extends React.Component {
	render(){
		let data = this.props.data;
		let auth = data.auth;
		let user = data.user;
		let response;

		if(user && user.name){
			response = (
				<div className="background--secondary floating-content">
					<h3 className="content-header">Profile</h3>
					<span className="user-data">{user.name}</span>
					<span className="user-data">{user.address}</span>
					<span className="user-data">{user.email}</span>
					<span className="user-data">{user.phone}</span>
				</div>
			)
		}
		else {
			response = (
				<div className="background--secondary floating-content">
					<h3 className="content-header">Profile</h3>
					<span className="user-data">It looks like you're not signed in.</span>
					<span className="user-data">
						Please sign in or sign up!&nbsp;&nbsp;
						<a title="Sign In" target="_blank" href={auth.cognitoLogin}>
							<i className="accent fa fa-sign-in"></i>
						</a>
					</span>
				</div>
			)
		}
		return response;
	}
}

export default UserComp;
