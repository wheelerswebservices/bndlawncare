
// External Dependencies
import React from 'react';
import ReactDOM from 'react-dom';
import jwt_decode from "jwt-decode";


// Internal Dependencies
import GalleryComp from './gallery.js';
import SocialComp from './social.js';
import UserComp from "./user";


{
	/*
     * ---------------------------------------------------------------------------
     * Authentication Variables
     */
}

const cognitoLogin = "https://bndlawncare33511.auth.us-east-1.amazoncognito.com/login"
	+ "?client_id=17k1bghjq8f110kp3lsj197lpn"
	+ "&redirect_uri=https://bndlawncare33511.com/"
	+ "&response_type=token"
	+ "&scope=email+openid+phone+profile";

const cognitoLogout = "https://bndlawncare33511.auth.us-east-1.amazoncognito.com/login"
	+ "?client_id=17k1bghjq8f110kp3lsj197lpn"
	+ "&logout_uri=https://bndlawncare33511.com/";

{
  /*
   * ---------------------------------------------------------------------------
   * Gallery Variables
   */
}

const galleryCompModel = {
	'size': 6
}

{
	/*
     * ---------------------------------------------------------------------------
     * Social Variables
     */
}

const cashapp = {
	'href': "https://cash.app/",
	'icon': "usd",
	'title': "Cashapp"
};

const facebook = {
	'href': "https://www.facebook.com/b.dlawncare33511",
	'icon': "facebook",
	'title': "Facebook"
};

const signin = {
	'href': cognitoLogin,
	'icon': "sign-in",
	'title': "Sign In"
};

const signout = {
	'href': cognitoLogout,
	'icon': "sign-out",
	'title': "Sign Out"
}

const square = {
	'href': "https://squareup.com/us/en",
	'icon': "credit-card",
	'title': "Square"
};

const top = {
	'href': "#top",
	'icon': "arrow-circle-up",
	'title': "Top"
};

const socialCompModelForHeaderSignin = {
	'icons': [signin, facebook]
}

const socialCompModelForHeaderSignout = {
	'icons': [signout, facebook]
}

const socialCompModelForFooter = {
	'icons': [facebook, cashapp, square, top]
}

{
	/*
     * ---------------------------------------------------------------------------
     * User Variables
     */
}

const urlParamStr = window.location.href.split('#');
const urlParamMap = new Map();

if(urlParamStr.length > 1){
	const urlParamArr = urlParamStr[1].split('&');
	for(let i = 0; i < urlParamArr.length; i++){
		const urlParamVal = urlParamArr[i].split('=');
		urlParamMap.set(urlParamVal[0], urlParamVal[1]);
	}
}

let user = {};
if(urlParamMap.has('id_token')){
	const jwtUser = jwt_decode(urlParamMap.get('id_token'));
	user = {
		'address': !!jwtUser.address ? jwtUser.address.formatted : undefined,
		'email': jwtUser.email,
		'name': jwtUser.name,
		'phone': jwtUser.phone_number
	}
}

const userCompModel = {
	'auth': {
		'cognitoLogin': cognitoLogin
	},
	'user': user
}

{
	/*
     * ---------------------------------------------------------------------------
     * Render Logic
     */
}

ReactDOM.render(
	<GalleryComp data={galleryCompModel} />,
	document.getElementById("photo-album"));

ReactDOM.render(
	<SocialComp data={!!userCompModel.user.name ? socialCompModelForHeaderSignout : socialCompModelForHeaderSignin} />,
	document.getElementById("social-header"));

ReactDOM.render(
	<SocialComp data={socialCompModelForFooter} />,
	document.getElementById("social-footer"));

ReactDOM.render(
	<UserComp data={userCompModel} />,
	document.getElementById("user-content"));
