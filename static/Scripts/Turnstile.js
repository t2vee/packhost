function _turnstileCb() {
    console.debug('_turnstileCb called');

    turnstile.render('#turnstileWidget', {
      sitekey: '0x4AAAAAAALM_WDREmQe2hsI',
      theme: 'dark',
    });
}