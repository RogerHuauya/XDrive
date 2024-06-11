describe('JavaScript Function Tests', () => {
    it('should call function', () => {
        cy.visit('');

        cy.window().then((win) => {
            win.getCsrfToken();
            win.calculateMd5();
            win.createMasterFile();
            win.uploadChunk();
        });
    });
});
