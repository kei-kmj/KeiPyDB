import { FilterPattern, Plugin } from 'vite';
import { VueJSXPluginOptions } from '@vue/babel-plugin-jsx';

interface FilterOptions {
    include?: FilterPattern;
    exclude?: FilterPattern;
}
interface Options extends VueJSXPluginOptions, FilterOptions {
    babelPlugins?: any[];
    /** @default ['defineComponent'] */
    defineComponentName?: string[];
    tsPluginOptions?: any;
}

declare function vueJsxPlugin(options?: Options): Plugin;

declare function vueJsxPluginCjs(this: unknown, options: Options): Plugin;

export { vueJsxPluginCjs as 'module.exports', type FilterOptions, type Options, vueJsxPlugin as default };
