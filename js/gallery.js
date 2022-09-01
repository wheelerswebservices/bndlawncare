import React from 'react';

class GalleryComp extends React.Component {
	render(){
		let data = this.props.data;
		let size = data.size;
        let photos = [];
        
        for (let i = 0; i < data.size; i++) {
            photos.push(<PhotoComp key={i} idx={i} type="before" />);
            photos.push(<PhotoComp key={i + size} idx={i} type="after" />);
        }
		return (
            <div className="photo-wrap">
                {photos}
            </div>
		)
	}
}

class PhotoComp extends React.Component {
  	render(){
        let idx = this.props.idx + 1;
        let type = this.props.type;
        
		return (
            <p className="photo">
                <img src={"images/" + type + "/" + idx + ".jpg"} />{type}
            </p>
        )
    }
}


export default GalleryComp;
export { PhotoComp };
