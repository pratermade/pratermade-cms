/* To avoid CSS expressions while still supporting IE 7 and IE 6, use this script */
/* The script tag referencing this file must be placed before the ending body tag. */

/* Use conditional comments in order to target IE 7 and older:
	<!--[if lt IE 8]><!-->
	<script src="ie7/ie7.js"></script>
	<!--<![endif]-->
*/

(function() {
	function addIcon(el, entity) {
		var html = el.innerHTML;
		el.innerHTML = '<span style="font-family: \'icomoon-aria\'">' + entity + '</span>' + html;
	}
	var icons = {
		'icon-login': '&#xe658;',
		'icon-mouse': '&#xe601;',
		'icon-home': '&#xe602;',
		'icon-newspaper': '&#xe603;',
		'icon-pencil': '&#xe604;',
		'icon-images': '&#xe605;',
		'icon-music': '&#xe606;',
		'icon-play': '&#xe607;',
		'icon-camera': '&#xe608;',
		'icon-connection': '&#xe609;',
		'icon-book': '&#xe60a;',
		'icon-library': '&#xe600;',
		'icon-profile': '&#xe60b;',
		'icon-file': '&#xe60c;',
		'icon-copy': '&#xe60d;',
		'icon-stack': '&#xe60e;',
		'icon-folder-open': '&#xe60f;',
		'icon-cart': '&#xe610;',
		'icon-coin': '&#xe611;',
		'icon-support': '&#xe612;',
		'icon-phone': '&#xe613;',
		'icon-address-book': '&#xe614;',
		'icon-envelope': '&#xe615;',
		'icon-location': '&#xe616;',
		'icon-clock': '&#xe617;',
		'icon-calendar': '&#xe618;',
		'icon-screen': '&#xe619;',
		'icon-mobile': '&#xe61a;',
		'icon-bubbles': '&#xe61b;',
		'icon-user': '&#xe61c;',
		'icon-users': '&#xe61d;',
		'icon-quotes-left': '&#xe61e;',
		'icon-search': '&#xe61f;',
		'icon-zoomin': '&#xe620;',
		'icon-zoomout': '&#xe621;',
		'icon-lock': '&#xe622;',
		'icon-cog': '&#xe623;',
		'icon-lab': '&#xe624;',
		'icon-accessibility': '&#xe625;',
		'icon-signup': '&#xe626;',
		'icon-cloud': '&#xe627;',
		'icon-earth2': '&#xe628;',
		'icon-link': '&#xe629;',
		'icon-flag': '&#xe62a;',
		'icon-attachment': '&#xe62b;',
		'icon-star': '&#xe62c;',
		'icon-heart': '&#xe62d;',
		'icon-info': '&#xe62e;',
		'icon-cancel-circle': '&#xe62f;',
		'icon-checkmark-circle': '&#xe630;',
		'icon-minus': '&#xe631;',
		'icon-plus': '&#xe632;',
		'icon-checkbox-checked': '&#xe633;',
		'icon-checkbox-unchecked': '&#xe634;',
		'icon-checkbox-partial': '&#xe635;',
		'icon-newtab': '&#xe636;',
		'icon-share': '&#xe637;',
		'icon-mail': '&#xe638;',
		'icon-googleplus': '&#xe639;',
		'icon-facebook': '&#xe63a;',
		'icon-instagram': '&#xe63b;',
		'icon-twitter': '&#xe63c;',
		'icon-feed': '&#xe63d;',
		'icon-youtube': '&#xe63e;',
		'icon-vimeo2': '&#xe63f;',
		'icon-flickr': '&#xe640;',
		'icon-picassa': '&#xe641;',
		'icon-dribbble': '&#xe642;',
		'icon-github': '&#xe643;',
		'icon-wordpress': '&#xe644;',
		'icon-blogger': '&#xe645;',
		'icon-tumblr': '&#xe646;',
		'icon-tux': '&#xe647;',
		'icon-apple': '&#xe648;',
		'icon-android': '&#xe649;',
		'icon-windows': '&#xe64a;',
		'icon-soundcloud': '&#xe64b;',
		'icon-linkedin': '&#xe64c;',
		'icon-delicious': '&#xe64d;',
		'icon-stumbleupon': '&#xe64e;',
		'icon-pinterest': '&#xe64f;',
		'icon-paypal': '&#xe650;',
		'icon-libreoffice': '&#xe651;',
		'icon-file-pdf': '&#xe652;',
		'icon-file-openoffice': '&#xe653;',
		'icon-file-word': '&#xe654;',
		'icon-file-excel': '&#xe655;',
		'icon-file-zip': '&#xe656;',
		'icon-file-powerpoint': '&#xe657;',
		'0': 0
		},
		els = document.getElementsByTagName('*'),
		i, c, el;
	for (i = 0; ; i += 1) {
		el = els[i];
		if(!el) {
			break;
		}
		c = el.className;
		c = c.match(/icon-[^\s'"]+/);
		if (c && icons[c[0]]) {
			addIcon(el, icons[c[0]]);
		}
	}
}());
