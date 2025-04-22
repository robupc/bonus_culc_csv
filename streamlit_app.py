import time
import streamlit as st
from typing import List, Dict, Tuple
from dataclasses import dataclass, field
import csv
import io

# データクラスの定義
@dataclass
class Node:
    # 文字列として保持するフィールド
    performance_month: str
    registration_date: str
    member_number: str
    bp: str
    registration_number: str
    name: str
    cancellation_date: str
    cancellation_reason: str
    registration_type: str
    calculation_title: int
    referrer_id: str
    referrer_name: str
    direct_upline_id: str
    direct_upline_name: str
    side: str
    
    # bool型に変換するフィールド
    mp: bool
    active: bool
    ba: bool
    
    # int型に変換するフィールド
    purchase_amount: int
    registration_fee: int
    main_product_amount: int
    main_product: int
    service_product: int
    direct_active: int
    binary_max: int
    previous_month_carryover_left: int
    previous_month_carryover_right: int
    binary_left: int
    binary_right: int
    cumulative_left: int
    cumulative_right: int
    next_month_carryover_left: int
    next_month_carryover_right: int
    commission_subtotal: int
    commission_total: int
    consumption_tax: int
    withholding_tax: int
    adjustment_outside_withholding: int
    previous_month_carryover: int
    transfer_fee: int
    transfer_amount: int
    next_month_carryover: int
    first_bonus: int
    binary_bonus: int
    product_free_bonus: int
    matching_bonus: int
    car_bonus: int
    house_bonus: int
    sharing_bonus: int
    status_match: int
    penalty: int
    bonus_adjustment: int
    children: List['Node'] = field(default_factory=list)
    bonus_point = 0
    total_bonus_point = 0
    past_calculation_title = 0

    def calculate_riseup_binary_bonus(self, bonus_params: Dict[str, float],binary_number) -> int:
        if self.calculation_title == 0:
            if binary_number <= 20:
                return bonus_params["level1"] * binary_number / 4
            else:
                return bonus_params["level1"] * 5
        elif self.calculation_title == 1:
            if binary_number <= 60:
                return bonus_params["level1"] * binary_number / 4
            else:
                return bonus_params["level1"] * 15
        elif self.calculation_title == 2:
            if binary_number <= 200:
                return bonus_params["level1"] * binary_number / 4
            else:
                return bonus_params["level1"] * 50
        elif self.calculation_title == 3:
            if binary_number <= 600:
                return bonus_params["level2"] * binary_number / 4
            else:
                return bonus_params["level2"] * 150
        elif self.calculation_title == 4:
            if binary_number <= 1000:
                return bonus_params["level3"] * binary_number / 4
            else:
                return bonus_params["level3"] * 250
        elif self.calculation_title == 5:
            if binary_number <= 2000:
                return bonus_params["level3"] * binary_number / 4
            else:
                return bonus_params["level3"] * 500
        elif self.calculation_title == 6:
            if binary_number <= 4000:
                return bonus_params["level3"] * binary_number / 4
            else:
                return bonus_params["level3"] * 1000
        elif self.calculation_title == 7:
            if binary_number <= 6000:
                return bonus_params["level4"] * binary_number / 4
            else:
                return bonus_params["level4"] * 1500
        elif self.calculation_title == 8:
            if binary_number <= 10000:
                return bonus_params["level4"] * binary_number / 4
            else:
                return bonus_params["level4"] * 2500
        elif self.calculation_title == 9:
            if binary_number <= 20000:
                return bonus_params["level4"] * binary_number / 4
            else:
                return bonus_params["level4"] * 5000
        elif self.calculation_title == 10:
            return bonus_params["level4"] * binary_number / 4

    def calculate_product_free_bonus(self, bonus_pf: Dict[str, int],binary_number) -> int:
        if binary_number >= 4 and binary_number < 8:
            return bonus_pf["pf4"]
        elif binary_number >= 8 and binary_number < 12:
            return bonus_pf["pf8"]
        elif binary_number >= 12 and binary_number < 16:
            return bonus_pf["pf12"]
        elif binary_number == 16:
            return bonus_pf["pf16"]
        else:
            return 0

    def calculate_matching_bonus(self, bonus_rise_params: Dict[str, float]) -> int:
        bonus = 0
        a_c = 0
        c = len(self.children)
        if c >= 1:
            for child in self.children:
                if child.active and child.ba and child.mp:
                    if child.cumulative_left <= child.cumulative_right:
                        child_binary_number = child.cumulative_left * 2
                    else:
                        child_binary_number = child.cumulative_right * 2
                    bonus += child.calculate_riseup_binary_bonus(bonus_rise_params, child_binary_number) * 0.15
                    bonus = int(bonus)
                    a_c += 1
                    if c >= 2:
                        for grandchild in child.children:
                            if grandchild.active and grandchild.ba and grandchild.mp:
                                if grandchild.cumulative_left <= grandchild.cumulative_right:
                                    grandchild_binary_number = grandchild.cumulative_left * 2
                                else:
                                    grandchild_binary_number = grandchild.cumulative_right * 2
                                bonus += grandchild.calculate_riseup_binary_bonus(bonus_rise_params, grandchild_binary_number) * 0.05
                                bonus = int(bonus)
                                a_c += 1
                                if c >= 3:
                                    for great_grandchild in grandchild.children:
                                        if great_grandchild.active and great_grandchild.ba and great_grandchild.mp:
                                            if great_grandchild.cumulative_left <= great_grandchild.cumulative_right:
                                                ggc_binary_number = great_grandchild.cumulative_left * 2
                                            else:
                                                ggc_binary_number = great_grandchild.cumulative_right * 2
                                            bonus += great_grandchild.calculate_riseup_binary_bonus(bonus_rise_params, ggc_binary_number) * 0.05
                                            bonus = int(bonus)
                                            a_c += 1
        return bonus,a_c

    def calculate_car_bonus(self) -> int:
        if self.calculation_title >= 4 and self.past_calculation_title >= 4:
            return 100000
        return 0

    def calculate_house_bonus(self) -> int:
        if self.calculation_title >= 5 and self.past_calculation_title >= 5:
            return 150000
        return 0

    def calculate_sharing_bonus(self, total_paid_points: int) -> int:
        if self.calculation_title == 3:
            return int(total_paid_points * 0.01)
        elif self.calculation_title >= 4:
            return int(total_paid_points * 0.002)
        return 0

# CSVファイルを読み込む関数
def read_csv_file(file):
    # バイナリデータを読み取り
    binary_data = file.read()
    # バイナリデータをUTF-8でデコード
    text_data = binary_data.decode('utf-8')
    # テキストデータをStringIOでラップ
    file_io = io.StringIO(text_data)
    # DictReaderに渡す
    reader = csv.DictReader(file_io)
    
    # 以降の処理（例としてノードリストを作成する部分）
    nodes = []
    TITLE_MAPPING = {
        'ゴールドメンバー': 1,
        'プラチナメンバー': 2,
        'サファイアメンバー': 3,
        'ルビーメンバー': 4,
        'エメラルドメンバー': 5,
        'ダイヤモンドメンバー': 6,
        'イエローダイヤモンドメンバー': 7,
        'ブルーダイヤモンドメンバー': 8,
        'レッドダイヤモンドメンバー': 9,
        'ブラックダイヤモンドメンバー': 10
    }
    
    for row in reader:
        try:
            title_value = TITLE_MAPPING.get(row['計算タイトル'], 0)
            node = Node(
                # 文字列として保持
                performance_month=row['実績月'],
                registration_date=row['登録日'],
                member_number=row['会員番号'],
                bp=row['BP'],
                registration_number=row['登録番号'],
                name=row['氏名'],
                cancellation_date=row['解約日'],
                cancellation_reason=row['解約理由'],
                registration_type=row['登録区分'],
                calculation_title=title_value,
                referrer_id=row['直上者ID'],
                referrer_name=row['紹介者名'],
                direct_upline_id=row['直上者ID'],
                direct_upline_name=row['直上者名'],
                side=row['左右'],
                
                # bool型に変換 ("TRUE" → True, "FALSE" → False)
                mp=row['MP'] == 'TRUE',
                active=row['アクティブ'] == 'TRUE',
                ba=row['BA'] == 'TRUE',
                
                # int型に変換 (空文字列は0に)
                purchase_amount=int(row['購入金額']) if row['購入金額'] else 0,
                registration_fee=int(row['登録料']) if row['登録料'] else 0,
                main_product_amount=int(row['メイン製品金額']) if row['メイン製品金額'] else 0,
                main_product=int(row['メイン製品']) if row['メイン製品'] else 0,
                service_product=int(row['サービス製品']) if row['サービス製品'] else 0,
                direct_active=int(row['直1アクティブ']) if row['直1アクティブ'] else 0,
                binary_max=int(row['バイナリー最大']) if row['バイナリー最大'] else 0,
                previous_month_carryover_left=int(row['前月繰越左']) if row['前月繰越左'] else 0,
                previous_month_carryover_right=int(row['前月繰越右']) if row['前月繰越右'] else 0,
                binary_left=int(row['バイナリー左']) if row['バイナリー左'] else 0,
                binary_right=int(row['バイナリー右']) if row['バイナリー右'] else 0,
                cumulative_left=int(row['累計左']) if row['累計左'] else 0,
                cumulative_right=int(row['累計右']) if row['累計右'] else 0,
                next_month_carryover_left=int(row['翌月繰越左']) if row['翌月繰越左'] else 0,
                next_month_carryover_right=int(row['翌月繰越右']) if row['翌月繰越右'] else 0,
                commission_subtotal=int(row['コミッション小計']) if row['コミッション小計'] else 0,
                commission_total=int(row['コミッション合計']) if row['コミッション合計'] else 0,
                consumption_tax=int(row['消費税']) if row['消費税'] else 0,
                withholding_tax=int(row['源泉']) if row['源泉'] else 0,
                adjustment_outside_withholding=int(row['源泉外調整金']) if row['源泉外調整金'] else 0,
                previous_month_carryover=int(row['前月繰越']) if row['前月繰越'] else 0,
                transfer_fee=int(row['振込手数料']) if row['振込手数料'] else 0,
                transfer_amount=int(row['振込額']) if row['振込額'] else 0,
                next_month_carryover=int(row['翌月繰越']) if row['翌月繰越'] else 0,
                first_bonus=int(row['ファーストボーナス']) if row['ファーストボーナス'] else 0,
                binary_bonus=int(row['バイナリーボーナス']) if row['バイナリーボーナス'] else 0,
                product_free_bonus=int(row['プロダクトフリーボーナス']) if row['プロダクトフリーボーナス'] else 0,
                matching_bonus=int(row['マッチングボーナス']) if row['マッチングボーナス'] else 0,
                car_bonus=int(row['カーボーナス']) if row['カーボーナス'] else 0,
                house_bonus=int(row['ハウスボーナス']) if row['ハウスボーナス'] else 0,
                sharing_bonus=int(row['シェアリングボーナス']) if row['シェアリングボーナス'] else 0,
                status_match=int(row['ステータスマッチ']) if row['ステータスマッチ'] else 0,
                penalty=int(row['ペナルティ—']) if row['ペナルティ—'] else 0,
                bonus_adjustment=int(row['ボーナス調整金']) if row['ボーナス調整金'] else 0
            )
            nodes.append(node)
        except ValueError as e:
            print(f"データ変換エラー: {e}, 行: {row}")
    return nodes

def calculate_all_bonuses(nodes: List[Node], bonus_rise_params: Dict[str, float], bonus_pf_params: Dict[str, int]) -> Dict[str, Tuple[int, int]]:
    total_paid_points = sum(node.purchase_amount for node in nodes)
    bonus_summary = {
        'riseup_bonus_30': [0, 0],
        'riseup_bonus_100': [0, 0],
        'riseup_bonus_1000': [0, 0],
        'riseup_bonus_10000': [0, 0],
        'product_free_bonus': [0, 0],
        'matching_bonus': [0, 0],
        'car_bonus': [0, 0],
        'house_bonus': [0, 0],
        'sharing_bonus': [0, 0]
    }

    #rank_lis = []
    #chi_lis = []
    for node in nodes:
        riseup_binary_bonus = 0
        product_free_bonus = 0
        matching_bonus = 0
        car_bonus = 0
        house_bonus = 0
        #rank_lis.append(node.calculation_title)
        #chi_lis.append(node.children)
        if node.active == False or node.mp == False or node.ba == False:
            continue

        else:
            if node.cumulative_left <= node.cumulative_right:
                binary_number = node.cumulative_left * 2
            else:
                binary_number = node.cumulative_right * 2
            riseup_binary_bonus = node.calculate_riseup_binary_bonus(bonus_rise_params, binary_number)
            if riseup_binary_bonus > 0:
                if 4 <= binary_number <= 60:
                    bonus_summary['riseup_bonus_30'][0] += riseup_binary_bonus
                    bonus_summary['riseup_bonus_30'][1] += 1
                elif 64 <= binary_number <= 200:
                    bonus_summary['riseup_bonus_100'][0] += riseup_binary_bonus
                    bonus_summary['riseup_bonus_100'][1] += 1
                elif 204 <= binary_number <= 2000:
                    bonus_summary['riseup_bonus_1000'][0] += riseup_binary_bonus
                    bonus_summary['riseup_bonus_1000'][1] += 1
                elif binary_number >= 2004:
                    bonus_summary['riseup_bonus_10000'][0] += riseup_binary_bonus
                    bonus_summary['riseup_bonus_10000'][1] += 1

            product_free_bonus = node.calculate_product_free_bonus(bonus_pf_params, binary_number)
            if product_free_bonus > 0:
                bonus_summary['product_free_bonus'][0] += product_free_bonus
                bonus_summary['product_free_bonus'][1] += 1

            matching_bonus,a_c = node.calculate_matching_bonus(bonus_rise_params)
            if matching_bonus > 0:
                bonus_summary['matching_bonus'][0] += matching_bonus
                bonus_summary['matching_bonus'][1] += a_c

            car_bonus = node.calculate_car_bonus()
            if car_bonus > 0:
                bonus_summary['car_bonus'][0] += car_bonus
                bonus_summary['car_bonus'][1] += 1

            house_bonus = node.calculate_house_bonus()
            if house_bonus > 0:
                bonus_summary['house_bonus'][0] += house_bonus
                bonus_summary['house_bonus'][1] += 1

        node.bonus_point = riseup_binary_bonus + product_free_bonus + matching_bonus + car_bonus + house_bonus
        node.total_bonus_point += node.bonus_point
    
    #st.write(rank_lis)
    #st.write(chi_lis)
    rank3 = 0
    rank4 = 0
    rank5 = 0
    rank6 = 0
    rank7 = 0
    rank8 = 0
    for node in nodes:
        if node.calculation_title == 3:
            rank3 += 1
        elif node.calculation_title == 4:
            rank4 += 1
        elif node.calculation_title == 5:
            rank5 += 1
        elif node.calculation_title == 6:
            rank6 += 1
        elif node.calculation_title == 7:
            rank7 += 1
        elif node.calculation_title == 8:
            rank8 += 1
        
    sharing_bonus = 0
    if rank3 >= 1:
        sharing_bonus += total_paid_points * 0.01
    if rank4 >= 1:
        sharing_bonus += total_paid_points * 0.002
    if rank5 >= 1:
        sharing_bonus += total_paid_points * 0.002
    if rank6 >= 1:
        sharing_bonus += total_paid_points * 0.002
    if rank7 >= 1:
        sharing_bonus += total_paid_points * 0.002
    if rank8 >= 1:
        sharing_bonus += total_paid_points * 0.002
    sharing_bonus = int(sharing_bonus)
    if sharing_bonus > 0:
        bonus_summary['sharing_bonus'][0] += sharing_bonus
        bonus_summary['sharing_bonus'][1] += 1
    node.bonus_point += sharing_bonus
    node.total_bonus_point += sharing_bonus

    return bonus_summary

def main():
    st.title("ボーナス計算シミュレーション")
    st.markdown("CSVを読み込んで、シミュレーションを実行します。")

    uploaded_file = st.file_uploader("CSVファイルのアップロード", type="csv")

    st.sidebar.header("シミュレーションパラメータ")
    
    num_simulations = st.sidebar.number_input("シミュレーション回数", min_value=1, value=2, step=1)

    st.sidebar.subheader("ライズアップボーナスの定数設定")
    bonus_rise_params = {
        "level1": st.sidebar.number_input("level1 (例: 3000)", value=3000.0),
        "level2": st.sidebar.number_input("level2 (例: 4000)", value=4000.0),
        "level3": st.sidebar.number_input("level3 (例: 5000)", value=5000.0),
        "level4": st.sidebar.number_input("level4 (例: 2000)", value=2000.0),
    }

    st.sidebar.subheader("プロダクトフリーボーナスの定数設定")
    bonus_pf_params = {
        "pf4": st.sidebar.number_input("pf4 (例: 10000)", value=10000, step=1000),
        "pf8": st.sidebar.number_input("pf8 (例: 7000)", value=7000, step=1000),
        "pf12": st.sidebar.number_input("pf12 (例: 4000)", value=4000, step=1000),
        "pf16": st.sidebar.number_input("pf16 (例: 1000)", value=1000, step=500),
    }

    if st.sidebar.button("計算開始"):
        if uploaded_file is not None:
            st.write("シミュレーション実行中・・・")
            nodes = read_csv_file(uploaded_file)
            st.write("ノード作成完了")
            # 以降の処理（省略）
        else:
            st.write("CSVファイルをアップロードしてください。")

        simulation_results = []
        # nodes を辞書に変換
        node_dict = {node.referrer_name: node for node in nodes}

        # 各 node を処理
        for node in nodes:
            if node.referrer_name:
                c_node = node_dict.get(node.name)
                if c_node:
                    node.children.append(c_node)
                    if node.name in node_dict:
                        del node_dict[node.name]

        st.write("親子関係構築完了")

        # シミュレーションループ
        for sim in range(num_simulations):
            total_bonus = 0
            st.write(f"#### シミュレーション {sim+1} 開始")
            bonus_summary = calculate_all_bonuses(nodes, bonus_rise_params, bonus_pf_params)
            total_bonus = sum(node.bonus_point for node in nodes)
            simulation_results.append((sim + 1, bonus_summary, total_bonus))

            # シミュレーションごとの結果を表示
            st.write(f"**シミュレーション{sim+1}のボーナス内訳 [合計金額, 件数]:**")
            st.json(bonus_summary)
            st.write(f"**シミュレーション{sim+1}の総ボーナス金額: {total_bonus}**")
            st.write(f"シミュレーション {sim+1} 完了")
            time.sleep(1)
            for node in nodes:
                node.bonus_point = 0
                node.past_calculation_title = node.calculation_title

if __name__ == "__main__":
    main()
