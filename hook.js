var BaseAddr;
function main() {
    rpc.exports = {
        start: function (processname) {
            console.log('脚本加载成功');
            BaseAddr = Module.getBaseAddress(processname);
            console.log("基址:", BaseAddr); 
            hooktest();
        }
    };
}
main();
