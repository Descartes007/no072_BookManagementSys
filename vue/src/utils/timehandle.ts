
import moment from "moment";

//对时间显示进行格式化处理，把10位时间戳转为指定格式显示
export const formatDateTime = (timestamp: number) => {
    return moment(timestamp * 1000).format('YYYY-MM-DD HH:mm:ss');
};