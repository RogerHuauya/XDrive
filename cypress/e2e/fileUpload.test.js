describe('JavaScript Function Tests', () => {
    beforeEach(() => {
        cy.visit('http://localhost:8000');
    });

    it('should call getCsrfToken function', () => {
        cy.window().then((win) => {
            cy.spy(win, 'getCsrfToken').as('getCsrfToken');
            win.getCsrfToken();
            cy.get('@getCsrfToken').should('have.been.called');
        });
    });

    it('should call calculateMd5 function', () => {
        cy.window().then((win) => {
            cy.spy(win, 'calculateMd5').as('calculateMd5');
            win.calculateMd5();
            cy.get('@calculateMd5').should('have.been.called');
        });
    });

    it('should call createMasterFile function', () => {
        cy.window().then((win) => {
            cy.spy(win, 'createMasterFile').as('createMasterFile');
            win.createMasterFile();
            cy.get('@createMasterFile').should('have.been.called');
        });
    });

    it('should call uploadChunk function', () => {
        cy.window().then((win) => {
            cy.spy(win, 'uploadChunk').as('uploadChunk');
            win.uploadChunk();
            cy.get('@uploadChunk').should('have.been.called');
        });
    });
});