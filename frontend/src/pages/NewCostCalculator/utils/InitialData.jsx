export const INITIAL_DATA = {
    creation_date: new Date().toISOString(),
    comment: "",
    unit_count: 1,
    printings: [
        {
        edition: {
            count: 0,
            list_size: { width: 420, height: 297, bleeds: 2 },
            density: 80,
            chroma: 1,
            lamination: 1,
            die_cutting: false,
        },
        production: {},
        comment: "",
        },
    ],
    operations: [
    ],
    economy: {
        tax_rate: 0.93,
        markup: 80,
    },
};