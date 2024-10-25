//解决跨域的问题
import webServerSrc from './src/components/global.vue'
const { defineConfig }=require('@vue/cli-service')
module.exports=defineConfig({
    //打包的时候一定要配置这几项
    publicPath: "./",
    outputDir: "dist",
    assetsDir: "static",

    transpileDependencies: true,
    devServer:{
        proxy:{
            '^/':{
                //target: 'http://127.0.0.1:8888',   //产生跨域的地址
                target: webServerSrc.webServerSrc,
                changeOrigin: true,
                pathRewrite:{
                    '^/':'/',
                }
            }
        }
    }
})