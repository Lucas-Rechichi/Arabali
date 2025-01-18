// For depicting an apostrophe with text inside JS files
export function correctApostrophe(string) {
    if (string.slice(0, -1) == 's') {
        return `${string}'`;
    } else {
        return `${string}'s`;
    };
};